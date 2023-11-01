<div align="center">
<h2><a href="https://arxiv.org/abs/2310.03013">Switch EMA: A Free Lunch for Better Flatness and Sharpness</a> </h2>

<!-- Introduction -->

## Introduction

Experonaital Moving Everage (EMA) is a widely used weight averaging technique to learn flat optima without any extra cost in deep neural network (DNN) optimization. Despite achieving better flatness, EMA might suffer from worse final performances.
We unveil the full potential of EMA with a single line of modification, i.e., switching the EMA parameters to the original model after each epoch, dubbed as Switch EMA. 
From both theoretical and empirical aspects, we demonstrate that Switch EMA can help DNNs to reach generalization optima that trade-off between flatness and sharpness.
To verify the effectiveness of Switch EMA, we conduct comparison experiments with discriminative and generative tasks on computer vision, including image classification, object detection and segmentation, contrastive learning, image generation, video prediction, and angle and age regression.
Comprehensive results show that Switch EMA is a truly free lunch for optimizing DNNs with better performances and convergence speeds.
