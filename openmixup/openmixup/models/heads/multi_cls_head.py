import torch.nn as nn
from mmcv.cnn import build_norm_layer
from mmcv.runner import BaseModule

from ..registry import HEADS
from ..utils import accuracy, MultiPooling


@HEADS.register_module
class MultiClsHead(BaseModule):
    """Multiple classifier heads (designed for fine-tuning).

    This head inputs feature maps from different stages of backbone, average
    pools each feature map to around 9000 dimensions, and then appends a
    linear classifier at each stage to predict corresponding class scores.

    Args:
        pool_type (str): 'adaptive' or 'specified'. If set to 'adaptive', use
            adaptive average pooling, otherwise use specified pooling params.
        in_indices (Sequence[int]): Input from which stages.
        with_last_layer_unpool (bool): Whether to unpool the features from
            last layer. Defaults to False.
        backbone (str): Specify which backbone to use. Defaults to 'resnet50'.
        norm_cfg (dict): dictionary to construct and config norm layer.
        num_classes (int): Number of classes. Defaults to 1000.
    """

    FEAT_CHANNELS = {
        'resnet18': [64, 64, 128, 256, 512],
        'resnet50': [64, 256, 512, 1024, 2048]
    }
    FEAT_LAST_UNPOOL = {
        'resnet50': 512 * 7 * 7,
        'resnet50': 2048 * 7 * 7
    }

    def __init__(self,
                 pool_type='adaptive',
                 in_indices=(0, ),
                 with_last_layer_unpool=False,
                 backbone='resnet50',
                 norm_cfg=dict(type='BN'),
                 num_classes=1000,
                 init_cfg=[
                    dict(type='Normal', std=0.01, layer='Linear'),
                    dict(type='Constant', val=1, layer=['_BatchNorm', 'GroupNorm'])
                 ]):
        super(MultiClsHead, self).__init__(init_cfg)
        assert norm_cfg['type'] in ['BN', 'SyncBN', 'GN', 'null']

        self.with_last_layer_unpool = with_last_layer_unpool
        self.with_norm = norm_cfg['type'] != 'null'

        self.criterion = nn.CrossEntropyLoss()
        self.post_process = nn.Softmax(dim=1)

        self.multi_pooling = MultiPooling(pool_type, in_indices, backbone)

        if self.with_norm:
            self.norms = nn.ModuleList([
                build_norm_layer(norm_cfg, self.FEAT_CHANNELS[backbone][l])[1]
                for l in in_indices
            ])

        self.fcs = nn.ModuleList([
            nn.Linear(self.multi_pooling.POOL_DIMS[backbone][l], num_classes)
            for l in in_indices
        ])
        if with_last_layer_unpool:
            self.fcs.append(
                nn.Linear(self.FEAT_LAST_UNPOOL[backbone], num_classes))

    def init_weights(self):
        if self.init_cfg is not None:
            super(MultiClsHead, self).init_weights()
            return
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m,
                            (nn.BatchNorm2d, nn.GroupNorm, nn.SyncBatchNorm)):
                if m.weight is not None:
                    nn.init.constant_(m.weight, 1)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x, post_process=False, **kwargs):
        """Forward head.

        Args:
            x (list[Tensor] | tuple[Tensor]): Feature maps of backbone,
                each tensor has shape (N, C, H, W).
            post_process (bool): Whether to do post processing (e.g., softmax)
                the inference results. It will convert the output to a list.

        Returns:
            list[Tensor]: A list of class scores.
        """
        assert isinstance(x, (list, tuple))
        if self.with_last_layer_unpool:
            last_x = x[-1]
        x = self.multi_pooling(x)
        if self.with_norm:
            x = [n(xx) for n, xx in zip(self.norms, x)]
        if self.with_last_layer_unpool:
            x.append(last_x)
        x = [xx.view(xx.size(0), -1) for xx in x]
        if not post_process:
            x = [fc(xx) for fc, xx in zip(self.fcs, x)]
        else:
            x = [self.post_process(fc(xx)) for fc, xx in zip(self.fcs, x)]
        return x

    def loss(self, cls_score, labels):
        """Compute the loss."""
        losses = dict()
        for i, s in enumerate(cls_score):
            # keys must contain "loss"
            losses['loss.{}'.format(i + 1)] = self.criterion(s, labels)
            losses['acc.{}'.format(i + 1)] = accuracy(s, labels)
        return losses
