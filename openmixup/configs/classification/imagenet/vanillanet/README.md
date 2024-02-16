# VanillaNet: the Power of Minimalism in Deep Learning

> [VanillaNet: the Power of Minimalism in Deep Learning](https://arxiv.org/abs/2305.12972)

## Abstract

At the heart of foundation models is the philosophy of "more is different", exemplified by the astonishing success in computer vision and natural language processing. However, the challenges of optimization and inherent complexity of transformer models call for a paradigm shift towards simplicity. In this study, we introduce VanillaNet, a neural network architecture that embraces elegance in design. By avoiding high depth, shortcuts, and intricate operations like self-attention, VanillaNet is refreshingly concise yet remarkably powerful. Each layer is carefully crafted to be compact and straightforward, with nonlinear activation functions pruned after training to restore the original architecture. VanillaNet overcomes the challenges of inherent complexity, making it ideal for resource-constrained environments. Its easy-to-understand and highly simplified architecture opens new possibilities for efficient deployment. Extensive experimentation demonstrates that VanillaNet delivers performance on par with renowned deep neural networks and vision transformers, showcasing the power of minimalism in deep learning. This visionary journey of VanillaNet has significant potential to redefine the landscape and challenge the status quo of foundation model, setting a new path for elegant and effective model design. Pre-trained models and codes are available at this https URL and this https URL.

<div align=center>
<img src="https://github.com/Westlake-AI/openmixup/assets/44519745/01efbf16-537b-4edf-b29f-aa3709607c4a" width="100%"/>
</div>

## Results and models

### ImageNet-1k

|      Model      |   Pretrain   | resolution | Params(M) | Flops(G) | Top-1 (%) |  Config  |   Download   |
| :-------------: | :----------: | :--------: | :-------: | :------: | :-------: | :------: | :----------: |
| VanillaNet-5\*  | From scratch |  224x224   |    15.5   |   8.34   |   72.49   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_5_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_5.pth) |
| VanillaNet-6\*  | From scratch |  224x224   |    32.5   |   9.99   |   76.36   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_6_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_6.pth) |
| VanillaNet-7\*  | From scratch |  224x224   |    32.8   |   11.65  |   77.98   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_7_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_7.pth) |
| VanillaNet-8\*  | From scratch |  224x224   |    37.1   |   13.29  |   79.13   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_8_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_8.pth) |
| VanillaNet-9\*  | From scratch |  224x224   |    41.4   |   14.96  |   79.87   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_9_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_9.pth) |
| VanillaNet-10\* | From scratch |  224x224   |    45.7   |   16.59  |   80.57   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_10_8xb128_fp16_ep300.py) | [model](https://github.com/huawei-noah/VanillaNet/releases/download/ckpt/vanillanet_10.pth) |
| VanillaNet-5    | From scratch |  224x224   |    15.5   |   8.34   |   76.28   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_5_adamw_8xb128_fp16_ep300.py) | model |
| VanillaNet-6    | From scratch |  224x224   |    32.5   |   9.99   |   77.21   | [config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/vanillanet/vanillanet_6_adamw_8xb128_fp16_ep300.py) | model |

We follow the original training setting provided by the original paper. *Models with * are converted from the [official repo](https://github.com/huawei-noah/VanillaNet).* We don't ensure these config files' training accuracy.

## Citation

```
@article{chen2023vanillanet,
  title={VanillaNet: the Power of Minimalism in Deep Learning},
  author={Chen, Hanting and Wang, Yunhe and Guo, Jianyuan and Tao, Dacheng},
  journal={arXiv preprint arXiv:2305.12972},
  year={2023}
}
```
