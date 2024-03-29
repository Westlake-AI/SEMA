<div align="center">
<h2><a href="https://arxiv.org/abs/2402.09240">Switch EMA: A Free Lunch for Better Flatness and Sharpness</a></h2>

[Siyuan Li](https://lupin1998.github.io/)<sup>\*,1,2,3</sup>, [Zicheng Liu](https://pone7.github.io/)<sup>\*,1,3</sup>, [Juanxi Tian](https://openreview.net/profile?id=~Juanxi_Tian1)<sup>\*,1</sup>, [Ge Wang](https://openreview.net/profile?id=~Ge_Wang3)<sup>\*,1,3</sup>, [Zedong Wang](https://zedongwang.netlify.app/)<sup>1</sup>, [Weiyang Jin](https://openreview.net/profile?id=~Weiyang_Jin1)<sup>1</sup>, [Di Wu](https://scholar.google.com/citations?user=egz8bGQAAAAJ&hl=zh-CN)<sup>1,3</sup>, [Tao Lin](https://scholar.google.co.id/citations?hl=zh-CN&user=QE9pa_cAAAAJ)<sup>1</sup>, [Chen Tan](https://chengtan9907.github.io/)<sup>1,3</sup>, [Yang Liu](https://scholar.google.co.id/citations?user=t1emSE0AAAAJ&hl=zh-CN)<sup>2</sup>, [Baigui Sun](https://scholar.google.co.id/citations?user=ZNhTHywAAAAJ&hl=zh-CN)<sup>2</sup>, [Stan Z. Li](https://scholar.google.com/citations?user=Y-nyLGIAAAAJ&hl=zh-CN)<sup>†,1</sup>

<sup>1</sup>[Westlake University](https://westlake.edu.cn/), <sup>2</sup>[Damo Academy](https://damo.alibaba.com/?language=en), <sup>3</sup>[Zhejiang University](https://www.zju.edu.cn/english/)
</div>

<p align="center">
<a href="https://arxiv.org/abs/2402.09240" alt="arXiv">
    <img src="https://img.shields.io/badge/arXiv-2402.09240-b31b1b.svg?style=flat" /></a>
<a href="https://github.com/Westlake-AI/SEMA/blob/main/LICENSE" alt="license">
    <img src="https://img.shields.io/badge/license-Apache--2.0-%23B7A800" /></a>
</p>

<!-- Introduction -->

## Introduction

Exponential Moving Average (EMA) is a widely used weight averaging (WA) regularization to learn flat optima for better generalizations without extra cost in deep neural network (DNN) optimization. Despite achieving better flatness, existing WA methods might fall into worse final performances or require extra test-time computations. This work unveils the full potential of EMA with a single line of modification, i.e., switching the EMA parameters to the original model after each epoch, dubbed as Switch EMA (SEMA). From both theoretical and empirical aspects, we demonstrate that SEMA can help DNNs to reach generalization optima that better trade-off between flatness and sharpness. To verify the effectiveness of SEMA, we conduct comparison experiments with discriminative, generative, and regression tasks on vision and language datasets, including image classification, self-supervised learning, object detection and segmentation, image generation, video prediction, attribute regression, and language modeling. Comprehensive results with popular optimizers and networks show that SEMA is a free lunch for DNN training by improving performances and boosting convergence speeds.

<p align="center">
<img src="https://github.com/Westlake-AI/openmixup/assets/44519745/5d6698c8-d189-4095-8076-d32ee59fdc57" width=95% 
class="center">
</p>

## Catalog

This repo is mainly based on [OpenMixup](https://github.com/Westlake-AI/openmixup) to implement classification, self-supervised learning, and regression tasks while using [MMDetection](https://github.com/open-mmlab/mmdetection/), DDPM, [OpenSTL](https://github.com/chengtan9907/OpenSTL), and [fairseq](https://github.com/facebookresearch/fairseq) for other tasks. **Please watch us for the latest release!**
<!-- Currently, this repo is reimplemented according to our official implementations in [OpenMixup](https://github.com/Westlake-AI/openmixup), and we are working on cleaning up experimental results and code implementations. Models are released in [GitHub](https://github.com/Westlake-AI/MogaNet/releases) / [Baidu Cloud](https://pan.baidu.com/s/1d5MTTC66gegehmfZvCQRUA?pwd=z8mf) / [Hugging Face](https://huggingface.co/MogaNet). -->

- [x] **Image Classification** on ImageNet-1K and CIFAR-100 in [OpenMixup](https://github.com/Westlake-AI/openmixup/tree/main/configs/classification/imagenet/). [[configs](classification/)]
- [x] **Self-supervised Learning** with Contrastive Learning Methods in [OpenMixup](https://github.com/Westlake-AI/openmixup/tree/main/configs/selfsup).
- [x] **Self-supervised Learning** with Masked Image Modeling Methods in [OpenMixup](https://github.com/Westlake-AI/openmixup/tree/main/configs/selfsup).
- [ ] **Object Detection and Segmentation** on COCO. [[code](detection/)]
- [ ] **Image Generation** on CIFAR-10 and CelebA-Align. [[code](image_generation/)]
- [ ] **Visual Regression** on AgeDB, IMDB-WIKI, and RCFMNIST in [OpenMixup](https://github.com/Westlake-AI/openmixup/tree/main/configs/regression).
- [ ] **Video Prediction** on Moving-MNIST [[code](video_prediction/)].

## Installation
Please check [INSTALL.md](./openmixup/docs/en/install.md) for installation instructions.

## Experimental Results
TODO!

<p align="right">(<a href="#top">back to top</a>)</p>

## License

This project is released under the [Apache 2.0 license](LICENSE).

## Acknowledgement

Our implementation is mainly based on the following codebases. We gratefully thank the authors for their wonderful works.

- [OpenMixup](https://github.com/Westlake-AI/openmixup): Open-source toolbox for visual representation learning.
- [MMDetection](https://github.com/open-mmlab/mmdetection): OpenMMLab Detection Toolbox and Benchmark.
- [OpenSTL](https://github.com/chengtan9907/OpenSTL): A Comprehensive Benchmark of Spatio-Temporal Predictive Learning.
- [fairseq](https://github.com/facebookresearch/fairseq): Facebook AI Research Sequence-to-Sequence Toolkit written in Python.

## Citation

If you find this repository helpful, please consider citing:
```
@inproceedings{Li2024SwitchEMA,
  title={Switch EMA: A Free Lunch for Better Flatness and Sharpness},
  author={Siyuan Li and Zicheng Liu and Juanxi Tian and Ge Wang and Zedong Wang and Weiyang Jin and Di Wu and Cheng Tan and Tao Lin and Yang Liu and Baigui Sun and Stan Z. Li},
  year={2024},
}
```

<p align="right">(<a href="#top">back to top</a>)</p>
