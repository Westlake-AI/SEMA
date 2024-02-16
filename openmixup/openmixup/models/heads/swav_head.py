# Copyright (c) OpenMMLab. All rights reserved.
import numpy as np
import torch
import torch.distributed as dist
import torch.nn as nn

from mmcv.cnn import normal_init
from mmcv.runner import BaseModule

from openmixup.third_party import distributed_sinkhorn
from ..registry import HEADS


class MultiPrototypes(BaseModule):
    """Multi-prototypes for SwAV head.

    Args:
        output_dim (int): The output dim from SwAV neck.
        num_prototypes (list[int]): The number of prototypes needed.
    """

    def __init__(self, output_dim, num_prototypes, init_cfg=None):
        super(MultiPrototypes, self).__init__(init_cfg)
        assert isinstance(num_prototypes, list)
        self.num_heads = len(num_prototypes)
        for i, k in enumerate(num_prototypes):
            self.add_module('prototypes' + str(i),
                            nn.Linear(output_dim, k, bias=False))

    def forward(self, x):
        out = []
        for i in range(self.num_heads):
            out.append(getattr(self, 'prototypes' + str(i))(x))
        return out


@HEADS.register_module()
class SwAVHead(BaseModule):
    """The head for SwAV.

    This head contains clustering and sinkhorn algorithms to compute Q codes.
    Part of the code is borrowed from:
    `<https://github.com/facebookresearch/swav`_.
    The queue is built in `core/hooks/swav_hook.py`.

    Args:
        feat_dim (int): feature dimension of the prototypes.
        sinkhorn_iterations (int): number of iterations in Sinkhorn-Knopp
            algorithm. Defaults to 3.
        epsilon (float): regularization parameter for Sinkhorn-Knopp algorithm.
            Defaults to 0.05.
        temperature (float): temperature parameter in training loss.
            Defaults to 0.1.
        crops_for_assign (list[int]): list of crops id used for computing
            assignments. Defaults to [0, 1].
        num_crops (list[int]): list of number of crops. Defaults to [2].
        num_prototypes (int): number of prototypes. Defaults to 3000.
        init_cfg (dict or list[dict], optional): Initialization config dict.
            Defaults to None.
    """

    def __init__(self,
                 feat_dim,
                 sinkhorn_iterations=3,
                 epsilon=0.05,
                 temperature=0.1,
                 crops_for_assign=[0, 1],
                 num_crops=[2],
                 num_prototypes=3000,
                 init_cfg=None,
                 **kwargs):
        super(SwAVHead, self).__init__(init_cfg)
        self.sinkhorn_iterations = sinkhorn_iterations
        self.epsilon = epsilon
        self.temperature = temperature
        self.crops_for_assign = crops_for_assign
        self.num_crops = num_crops
        self.use_queue = False
        self.queue = None
        self.world_size = dist.get_world_size() if dist.is_initialized() else 1

        # prototype layer
        self.prototypes = None
        if isinstance(num_prototypes, list):
            self.prototypes = MultiPrototypes(feat_dim, num_prototypes)
        elif num_prototypes > 0:
            self.prototypes = nn.Linear(feat_dim, num_prototypes, bias=False)
        assert self.prototypes is not None

    def init_weights(self, init_linear='normal', std=0.01, bias=0.):
        if self.init_cfg is not None:
            super(SwAVHead, self).init_weights()
        else:
            if init_linear == 'normal':
                normal_init(self.prototypes, std=std, bias=bias)

    def forward(self, x, **kwargs):
        """Forward head of swav to compute the loss.

        Args:
            x (Tensor): NxC input features.
        Returns:
            dict[str, Tensor]: A dictionary of loss components.
        """
        # normalize the prototypes
        with torch.no_grad():
            w = self.prototypes.weight.data.clone()
            w = nn.functional.normalize(w, dim=1, p=2)
            self.prototypes.weight.copy_(w)

        embedding, output = x, self.prototypes(x)
        embedding = embedding.detach()

        bs = int(embedding.size(0) / sum(self.num_crops))
        loss = 0
        for i, crop_id in enumerate(self.crops_for_assign):
            with torch.no_grad():
                out = output[bs * crop_id:bs * (crop_id + 1)].detach()
                # time to use the queue
                if self.queue is not None:
                    if self.use_queue or not torch.all(self.queue[i,
                                                                  -1, :] == 0):
                        self.use_queue = True
                        out = torch.cat(
                            (torch.mm(self.queue[i],
                                      self.prototypes.weight.t()), out))
                    # fill the queue
                    self.queue[i, bs:] = self.queue[i, :-bs].clone()
                    self.queue[i, :bs] = embedding[crop_id * bs:(crop_id + 1) *
                                                   bs]

                # get assignments (batch_size * num_prototypes)
                q = distributed_sinkhorn(out, self.sinkhorn_iterations,
                                         self.world_size, self.epsilon)[-bs:]

            # cluster assignment prediction
            subloss = 0
            for v in np.delete(np.arange(np.sum(self.num_crops)), crop_id):
                x = output[bs * v:bs * (v + 1)] / self.temperature
                subloss -= torch.mean(
                    torch.sum(q * nn.functional.log_softmax(x, dim=1), dim=1))
            loss += subloss / (np.sum(self.num_crops) - 1)
        loss /= len(self.crops_for_assign)

        return dict(loss=loss)
