# Applying Switch EMA to Object Detection

This repo is a PyTorch implementation of applying **Switch EMA** to object detaction and instance segmentation with [Mask R-CNN](https://arxiv.org/abs/1703.06870) and [RetinaNet](https://arxiv.org/abs/1708.02002) on [COCO](https://arxiv.org/abs/1405.0312). The code is based on [MMDetection](https://github.com/open-mmlab/mmdetection/tree/v2.26.0).

## Note

Please note that we simply follow the hyper-parameters of [PVT](https://github.com/whai362/PVT/tree/v2/detection) and [ConvNeXt](https://github.com/facebookresearch/ConvNeXt), which may not be the optimal ones for MogaNet. Feel free to tune the hyper-parameters to get better performance.

## Environement Setup

Install [MMDetection](https://github.com/open-mmlab/mmdetection/) from souce code, or follow the following steps. This experiment uses MMDetection>=2.19.0, and we reproduced the results with [MMDetection v2.26.0](https://github.com/open-mmlab/mmdetection/tree/v2.26.0) and Pytorch==1.10.
```
pip install openmim
mim install mmcv-full
pip install mmdet
```

Apex (optional) for Pytorch<=1.6.0:
```
git clone https://github.com/NVIDIA/apex
cd apex
python setup.py install --cpp_ext --cuda_ext --user
```

By default, we run experiments with fp32 or fp16 (Apex). If you would like to disable apex, modify the type of runner as `EpochBasedRunner` and comment out the following code block in the configuration files:
```
fp16 = None
optimizer_config = dict(
    type="DistOptimizerHook",
    update_interval=1,
    grad_clip=None,
    coalesce=True,
    bucket_size_mb=-1,
    use_fp16=True,
)
```

## Data preparation

Download [COCO2017](https://cocodataset.org/#download) and prepare COCO experiments according to the guidelines in [MMDetection](https://github.com/open-mmlab/mmdetection/).

<p align="right">(<a href="#top">back to top</a>)</p>

## Training

We train the model on a single node with 8 GPUs (a batch size of 16) by default. Start training with the config as:
```bash
PORT=29001 bash dist_train.sh /path/to/config 8
```

## Evaluation

To evaluate the trained model on a single node with 8 GPUs, run:
```bash
bash dist_test.sh /path/to/config /path/to/checkpoint 8 --out results.pkl --eval bbox # or `bbox segm`
```

<!-- ## Citation

If you find this repository helpful, please consider citing:
```
@article{Li2022MogaNet,
  title={Efficient Multi-order Gated Aggregation Network},
  author={Siyuan Li and Zedong Wang and Zicheng Liu and Cheng Tan and Haitao Lin and Di Wu and Zhiyuan Chen and Jiangbin Zheng and Stan Z. Li},
  journal={ArXiv},
  year={2022},
  volume={abs/2211.03295}
}
``` -->

## Acknowledgment

Our implementation is mainly based on the following codebases. We gratefully thank the authors for their wonderful works.

- [MMDetection](https://github.com/open-mmlab/mmdetection)
- [PVT detection](https://github.com/whai362/PVT/tree/v2/detection)
- [ConvNeXt](https://github.com/facebookresearch/ConvNeXt)
- [PoolFormer](https://github.com/sail-sg/poolformer)

<p align="right">(<a href="#top">back to top</a>)</p>
