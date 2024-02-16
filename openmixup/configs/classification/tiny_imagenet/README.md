# Mixup Classification Benchmark on Tiny-ImageNet

> [A Downsampled Variant of ImageNet as an Alternative to the CIFAR datasets](https://arxiv.org/abs/1707.08819)

## Abstract

The original ImageNet dataset is a popular large-scale benchmark for training Deep Neural Networks. Since the cost of performing experiments (e.g, algorithm design, architecture search, and hyperparameter tuning) on the original dataset might be prohibitive, we propose to consider a downsampled version of ImageNet. In contrast to the CIFAR datasets and earlier downsampled versions of ImageNet, our proposed ImageNet32×32 (and its variants ImageNet64×64 and ImageNet16×16) contains exactly the same number of classes and images as ImageNet, with the only difference that the images are downsampled to 32×32 pixels per image (64×64 and 16×16 pixels for the variants, respectively). Experiments on these downsampled variants are dramatically faster than on the original ImageNet and the characteristics of the downsampled datasets with respect to optimal hyperparameters appear to remain similar. The proposed datasets and scripts to reproduce our results are available at [this http URL](http://image-net.org/download-images) and [this https URL](https://github.com/PatrykChrabaszcz/Imagenet32_Scripts).

<div align=center>
<img src="https://user-images.githubusercontent.com/44519745/185863281-0167711e-2909-4233-8508-76641f7036e3.png" width="100%"/>
</div>

## Results and models

### Getting Started

* You can start training and evaluating with a config file. An example with a single GPU,
  ```shell
  CUDA_VISIBLE_DEVICES=1 PORT=29001 bash tools/dist_train.sh ${CONFIG_FILE} 1
  ```
* Please refer to config files for experiment details: [various mixups](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/mixups/), [AutoMix](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/automix/), [SAMix](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/samix/). As for config files of various mixups, please modify `max_epochs` and `mix_mode` in `auto_train_mixups.py` to generate configs and bash scripts. Here is an example of using Mixup and CutMix with switching probabilities of $\{0.4, 0.6\}$ based on [base_config](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/mixups/basic/r18_mixups_CE_none.py).
  ```python
  model = dict(
      alpha=[0.1, 1],  # list of alpha
      mix_mode=["mixup", "cutmix"],  # list of chosen mixup modes
      mix_prob=[0.4, 0.6],  # list of applying probs (sum=1), `None` for random applying
      mix_repeat=1,  # times of repeating mixups in each iteration
  )
  ```

### Tiny-ImageNet

**Setup**

* This benchmark largely follows [PuzzleMix](https://arxiv.org/abs/2009.06962) using CIFAR varient of ResNet. All compared methods adopt ResNet-18 and ResNeXt-50 (32x4d) architectures training 400 epochs on [Tiny-ImageNet](https://www.kaggle.com/c/tiny-imagenet). The training and testing image size is 64 (no CenterCrop in testing) and we search $\alpha$ in $Beta(\alpha, \alpha)$ for all compared methods.
* As for mixup variants requiring some special components, we provide examples based on ResNet-18: [AttentiveMix+](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/mixups/r18_attentivemix_CE_none.py) and [PuzzleMix](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/tiny_imagenet/mixups/r18_puzzlemix_CE_soft.py).
* The **median** of top-1 accuracy in the last 10 training epochs is reported. Notice that 📖 denotes original results reproduced by official implementations.

| Backbones                                                       | ResNet-18 top-1 | ResNeXt-50 top-1 |
|-----------------------------------------------------------------|:---------------:|:----------------:|
| Vanilla                                                         |      61.68      |       65.04      |
| MixUp [[ICLR'2018](https://arxiv.org/abs/1710.09412)]           |      63.86      |       66.36      |
| CutMix [[ICCV'2019](https://arxiv.org/abs/1905.04899)]          |      65.53      |       66.47      |
| ManifoldMix [[ICML'2019](https://arxiv.org/abs/1806.05236)]     |      64.15      |       67.30      |
| SmoothMix [[CVPRW'2020](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w45/Lee_SmoothMix_A_Simple_Yet_Effective_Data_Augmentation_to_Train_Robust_CVPRW_2020_paper.pdf)] |   66.65   |    69.65   |
| SaliencyMix [[ICLR'2021](https://arxiv.org/abs/2006.01791)]     |      64.60      |       66.55      |
| AttentiveMix+ [[ICASSP'2020]](https://arxiv.org/abs/2003.13048) |      64.85      |       67.42      |
| FMix [[Arixv'2020](https://arxiv.org/abs/2002.12047)]           |      63.47      |       65.08      |
| PuzzleMix [[ICML'2020](https://arxiv.org/abs/2009.06962)]       |      65.81      |       67.83      |
| ResizeMix [[Arixv'2020](https://arxiv.org/abs/2012.11101)]      |      63.74      |       65.87      |
| GridMix [PR'2021](https://www.sciencedirect.com/science/article/pii/S0031320320303976) |   65.14   |    66.53   |
| AutoMix [[ECCV'2022](https://arxiv.org/abs/2103.13027)]         |      67.33      |       70.72      |
| SAMix [[Arxiv'2021](https://arxiv.org/abs/2111.15454)]          |      68.89      |       72.18      |

We summarize mixup benchmarks in [Model Zoo](https://github.com/Westlake-AI/openmixup/tree/main/docs/en/model_zoos/Model_Zoo_sup.md).


## Citation

Please refer to the original paper of [Tiny-ImageNet](https://arxiv.org/abs/1707.08819) for dataset information, and refer to [AutoMix](https://arxiv.org/abs/2103.13027) for experiment details.

```bibtex
@article{Chrabaszcz2017tinyimagenet,
  title={A Downsampled Variant of ImageNet as an Alternative to the CIFAR datasets},
  author={Patryk Chrabaszcz and Ilya Loshchilov and Frank Hutter},
  journal={ArXiv},
  year={2017},
  volume={abs/1707.08819}
}
```
