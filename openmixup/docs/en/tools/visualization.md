# Visualization

- [Visualization](#visualization)
  - [Learning Rate Schedule Visualization](#learning-rate-schedule-visualization)
  - [Class Activation Map Visualization](#class-activation-map-visualization)
  - [Loss Landscape Visualization](#loss-landscape-visualization)
  - [FAQs](#faqs)


## Learning Rate Schedule Visualization

```bash
python tools/visualizations/vis_lr.py \
    ${CONFIG_FILE} \
    --dataset-size ${DATASET_SIZE} \
    --ngpus ${NUM_GPUs}
    --save-path ${SAVE_PATH} \
    --title ${TITLE} \
    --style ${STYLE} \
    --window-size ${WINDOW_SIZE}
    --cfg-options
```

**Description of all arguments**：

- `config` :  The path of a model config file.
- `dataset-size` : The size of the datasets. If set，`build_dataset` will be skipped and `${DATASET_SIZE}` will be used as the size. Default to use the function `build_dataset`.
- `ngpus` : The number of GPUs used in training, default to be 1.
- `save-path` : The learning rate curve plot save path, default not to save.
- `title` : Title of figure. If not set, default to be config file name.
- `style` : Style of plt. If not set, default to be `whitegrid`.
- `window-size`: The shape of the display window. If not specified, it will be set to `12*7`. If used, it must be in the format `'W*H'`.
- `cfg-options` : Modifications to the configuration file, refer to [Tutorial 1: Learn about Configs](https://openmixup.readthedocs.io/en/latest/tutorials/0_config.html).

```{note}
Loading annotations maybe consume much time, you can directly specify the size of the dataset with `dataset-size` to save time.
```

**Examples**：

```bash
python tools/visualizations/vis_lr.py configs/classification/imagenet/resnet/resnet50_4xb64_step_ep100.py
```

When using ImageNet, directly specify the size of ImageNet, as below:

```bash
python tools/visualizations/vis_lr.py configs/classification/imagenet/resnet/resnet50_4xb64_step_ep100.py --dataset-size 1281167 --ngpus 4 --save-path ./resnet50_4xb64_step_ep100.jpg
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Class Activation Map Visualization

OpenMixup provides `tools\visualizations\vis_cam.py` tool to visualize class activation map. Please use `pip install "grad-cam>=1.3.6"` command to install [pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam). The implementation is modified according to [MMClassification](https://github.com/open-mmlab/mmclassification) (thanks to their contributions).

The supported methods are as follows:

| Method       | What it does                                                                                                                 |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| GradCAM      | Weight the 2D activations by the average gradient                                                                            |
| GradCAM++    | Like GradCAM but uses second order gradients                                                                                 |
| XGradCAM     | Like GradCAM but scale the gradients by the normalized activations                                                           |
| EigenCAM     | Takes the first principle component of the 2D Activations (no class discrimination, but seems to give great results)         |
| EigenGradCAM | Like EigenCAM but with class discrimination: First principle component of Activations\*Grad. Looks like GradCAM, but cleaner |
| LayerCAM     | Spatially weight the activations by positive gradients. Works better especially in lower layers                              |

**Command**：

```bash
python tools/visualizations/vis_cam.py \
    ${IMG} \
    ${CONFIG_FILE} \
    ${CHECKPOINT} \
    [--target-layers ${TARGET-LAYERS}] \
    [--preview-model] \
    [--method ${METHOD}] \
    [--target-category ${TARGET-CATEGORY}] \
    [--save-path ${SAVE_PATH}] \
    [--vit-like] \
    [--num-extra-tokens ${NUM-EXTRA-TOKENS}]
    [--aug_smooth] \
    [--eigen_smooth] \
    [--device ${DEVICE}] \
    [--cfg-options ${CFG-OPTIONS}]
```

**Description of all arguments**：

- `img` : The target picture path.
- `config` : The path of the model config file.
- `checkpoint` : The path of the checkpoint.
- `--target-layers` : The target layers to get activation maps, one or more network layers can be specified. If not set, use the norm layer of the last block.
- `--preview-model` : Whether to print all network layer names in the model.
- `--method` : Visualization method, supports `GradCAM`, `GradCAM++`, `XGradCAM`, `EigenCAM`, `EigenGradCAM`, `LayerCAM`, which is case insensitive. Defaults to `GradCAM`.
- `--target-category` : Target category, if not set, use the category detected by the given model.
- `--save-path` : The path to save the CAM visualization image. If not set, the CAM image will not be saved.
- `--vit-like` : Whether the network is ViT-like network.
- `--num-extra-tokens` : The number of extra tokens in ViT-like backbones. If not set, use num_extra_tokens the backbone.
- `--aug_smooth` : Whether to use TTA(Test Time Augment) to get CAM.
- `--eigen_smooth` : Whether to use the principal component to reduce noise.
- `--device` : The computing device used. Default to 'cpu'.
- `--cfg-options` : Modifications to the configuration file, refer to [Tutorial 1: Learn about Configs](https://openmixup.readthedocs.io/en/latest/tutorials/0_config.html).

```{note}
The argument `--preview-model` can view all network layers names in the given model. It will be helpful if you know nothing about the model layers when setting `--target-layers`.
```

**Examples(CNN)**：

Here are some examples of `target-layers` in ResNet-50, which can be any module or layer:

- `'backbone.layer4'` means the output of the forth ResLayer.
- `'backbone.layer4.2'` means the output of the third BottleNeck block in the forth ResLayer.
- `'backbone.layer4.2.conv1'` means the output of the `conv1` layer in above BottleNeck block.

```{note}
For `ModuleList` or `Sequential`, you can also use the index to specify which sub-module is the target layer.

For example, the `backbone.layer4[-1]` is the same as `backbone.layer4.2` since `layer4` is a `Sequential` with three sub-modules.
```

1. Use different methods to visualize CAM for `ResNet50`, the `target-category` is the predicted result by the given checkpoint, using the default `target-layers`.

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/bird.JPEG \
       configs/classification/imagenet/resnet/resnet50_4xb64_step_ep100.py \
       https://download.openmmlab.com/mmclassification/v0/resnet/resnet50_batch256_imagenet_20200708-cfb998bf.pth \
       --method GradCAM
       # GradCAM++, XGradCAM, EigenCAM, EigenGradCAM, LayerCAM
   ```

   | Image                                | GradCAM                                 | GradCAM++                                 | EigenGradCAM                                 | LayerCAM                                 |
   | ------------------------------------ | --------------------------------------- | ----------------------------------------- | -------------------------------------------- | ---------------------------------------- |
   | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144429496-628d3fb3-1f6e-41ff-aa5c-1b08c60c32a9.JPEG' height="auto" width="160" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/147065002-f1c86516-38b2-47ba-90c1-e00b49556c70.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/147065119-82581fa1-3414-4d6c-a849-804e1503c74b.jpg' height="auto" width="150"></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/147065096-75a6a2c1-6c57-4789-ad64-ebe5e38765f4.jpg' height="auto" width="150"></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/147065129-814d20fb-98be-4106-8c5e-420adcc85295.jpg' height="auto" width="150"></div> |

2. Use different `target-category` to get CAM from the same picture. In `ImageNet` dataset, the category 238 is 'Greater Swiss Mountain dog', the category 281 is 'tabby, tabby cat'.

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/cat-dog.png \
       configs/classification/imagenet/resnet/resnet50_4xb64_step_ep100.py \
       https://download.openmmlab.com/mmclassification/v0/resnet/resnet50_batch256_imagenet_20200708-cfb998bf.pth \
       --target-layers 'backbone.layer4.2' \
       --method GradCAM \
       --target-category 238
       # --target-category 281
   ```

   | Category | Image                                          | GradCAM                                          | XGradCAM                                          | LayerCAM                                          |
   | -------- | ---------------------------------------------- | ------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------- |
   | Dog      | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144429526-f27f4cce-89b9-4117-bfe6-55c2ca7eaba6.png' height="auto" width="165" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144433562-968a57bc-17d9-413e-810e-f91e334d648a.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144433853-319f3a8f-95f2-446d-b84f-3028daca5378.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144433937-daef5a69-fd70-428f-98a3-5e7747f4bb88.jpg' height="auto" width="150" ></div> |
   | Cat      | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144429526-f27f4cce-89b9-4117-bfe6-55c2ca7eaba6.png' height="auto" width="165" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144434518-867ae32a-1cb5-4dbd-b1b9-5e375e94ea48.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144434603-0a2fd9ec-c02e-4e6c-a17b-64c234808c56.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144434623-b4432cc2-c663-4b97-aed3-583d9d3743e6.jpg' height="auto" width="150" ></div> |

3. Use `--eigen-smooth` and `--aug-smooth` to improve visual effects.

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/bird.JPEG \
       configs/classification/imagenet/resnet/resnet50_4xb64_step_ep100.py \
       https://download.openmmlab.com/mmclassification/v0/resnet/resnet50_batch256_imagenet_20200708-cfb998bf.pth \
       --target-layers 'backbone.layer4.2' \
       --method LayerCAM \
       --eigen-smooth --aug-smooth
   ```

   | Image                                | LayerCAM                                | eigen-smooth                                | aug-smooth                                | eigen&aug                                 |
   | ------------------------------------ | --------------------------------------- | ------------------------------------------- | ----------------------------------------- | ----------------------------------------- |
   | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144557492-98ac5ce0-61f9-4da9-8ea7-396d0b6a20fa.jpg' height="auto" width="160"></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144557541-a4cf7d86-7267-46f9-937c-6f657ea661b4.jpg'  height="auto" width="145" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144557547-2731b53e-e997-4dd2-a092-64739cc91959.jpg'  height="auto" width="145" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144557545-8189524a-eb92-4cce-bf6a-760cab4a8065.jpg'  height="auto" width="145" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144557548-c1e3f3ec-3c96-43d4-874a-3b33cd3351c5.jpg'  height="auto" width="145" ></div> |

**Examples(Transformer)**：

Here are some examples:

- `'backbone.norm3'` for Swin-Transformer;
- `'backbone.layers[-1].ln1'` for ViT;

For ViT-like networks, such as ViT, T2T-ViT and Swin-Transformer, the features are flattened. And for drawing the CAM, we need to specify the `--vit-like` argument to reshape the features into square feature maps.

Besides the flattened features, some ViT-like networks also add extra tokens like the class token in ViT and T2T-ViT, and the distillation token in DeiT. In these networks, the final classification is done on the tokens computed in the last attention block, and therefore, the classification score will not be affected by other features and the gradient of the classification score with respect to them, will be zero. Therefore, you shouldn't use the output of the last attention block as the target layer in these networks.

To exclude these extra tokens, we need know the number of extra tokens. Almost all transformer-based backbones in MMClassification have the `num_extra_tokens` attribute. If you want to use this tool in a new or third-party network that don't have the `num_extra_tokens` attribute, please specify it the `--num-extra-tokens` argument.

1. Visualize CAM for `Swin Transformer`, using default `target-layers`:

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/bird.JPEG \
       configs/classification/imagenet/swin_transformer/swin_tiny_8xb128_fp16_ep300.py \
       https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_tiny_224_b16x64_300e_imagenet_20210616_090925-66df6be6.pth \
       --vit-like
   ```

2. Visualize CAM for `Vision Transformer(ViT)`:

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/bird.JPEG \
       configs/classification/imagenet/deit/deit_base_8xb128_ep300.py \
       https://download.openmmlab.com/mmclassification/v0/deit/deit-base_3rdparty_pt-16xb64_in1k_20211124-6f40c188.pth \
       --vit-like \
       --target-layers 'backbone.layers[-1].ln1'
   ```

3. Visualize CAM for `T2T-ViT`:

   ```shell
   python tools/visualizations/vis_cam.py \
       demo/bird.JPEG \
       configs/classification/imagenet/t2t_vit/t2t_vit_tiny_14_ema_8xb64_ep310.py \
       https://download.openmmlab.com/mmclassification/v0/t2t-vit/t2t-vit-t-14_3rdparty_8xb64_in1k_20210928-b7c09b62.pth \
       --vit-like \
       --target-layers 'backbone.encoder[-1].ln1'
   ```

| Image                                   | ResNet50                                   | ViT                                    | Swin                                    | T2T-ViT                                    |
| --------------------------------------- | ------------------------------------------ | -------------------------------------- | --------------------------------------- | ------------------------------------------ |
| <div align=center><img src='https://user-images.githubusercontent.com/18586273/144429496-628d3fb3-1f6e-41ff-aa5c-1b08c60c32a9.JPEG' height="auto" width="165" ></div> | <div align=center><img src=https://user-images.githubusercontent.com/18586273/144431491-a2e19fe3-5c12-4404-b2af-a9552f5a95d9.jpg  height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144436218-245a11de-6234-4852-9c08-ff5069f6a739.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144436168-01b0e565-442c-4e1e-910c-17c62cff7cd3.jpg' height="auto" width="150" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/18586273/144436198-51dbfbda-c48d-48cc-ae06-1a923d19b6f6.jpg' height="auto" width="150" ></div> |

<p align="right">(<a href="#top">back to top</a>)</p>

## Loss Landscape Visualization

OpenMixup provides `tools\visualizations\vis_loss_landscape.py` tool to visualize loss landscapes of classification models. Please use `pip install h5py` command to install [h5py](http://docs.h5py.org/en/stable/build.html#install). The implementation is borrowed and modified from [loss-landscape](https://github.com/tomgoldstein/loss-landscape) in [Visualizing the Loss Landscape of Neural Nets](https://arxiv.org/abs/1712.09913). Thanks to their contributions.

We run [vis_loss_landscape.py](https://github.com/Westlake-AI/openmixup/tree/main/tools/visualizations/vis_loss_landscape.py) by [dist_vis_loss.sh](https://github.com/Westlake-AI/openmixup/tree/main/tools/visualizations/dist_vis_loss.sh) as DDP testing. This tool calculates and visualizes the loss surface along random direction(s) near the optimal parameters in parallel with multiple GPUs. To avoid the blocking error from `h5py`, you can use `export HDF5_USE_FILE_LOCKING=FALSE` before running the visualization experiment.

**Command**

```bash
bash tools/visualizations/dist_vis_loss.sh \
    ${CONFIG_FILE} \
    ${GPUS} \
    ${CHECKPOINT} \
    [--plot_mode ${surface | trajectory | surface+trajectory}] \
    [--dir_type ${weights | states}] \
    [--dir_type ${weights | states}] \
    [--x ${xmin:x_max:xnum}] \
    [--y ${ymin:y_max:ynum}] \
    [--xnorm ${filter | layer | weight}] \
    [--ynorm ${filter | layer | weight}] \
    [--xignore ${biasbn}] \
    [--yignore ${biasbn}] \
    [--cfg-options ${CFG-OPTIONS}]
```

**Description of all arguments**：

- `config` : The path of the model config file.
- `gpu` : The number of GPUs to evaluate the model.
- `checkpoint` : The path of the checkpoint.
- `--plot_mode` : The plot mode of loss landscape ('surface' | 'trajectory' | 'surface+trajectory').
- `--model_file2` : Using (model_file2 - model_file1) as the xdirection.
- `--model_file3` : Using (model_file3 - model_file1) as the ydirection.
- `--dir_file` : Specify the name of direction file, or the path to a direction file.
- `--dir_type` : The plotting direction type ('weights' | 'states'). Note that 'states' indicates the direction contains dimensions for all parameters as well as the statistics of the BN layers (`running_mean` and `running_var`), while 'weights' indicates the direction has the same dimensions as the learned parameters, including bias and parameters in the BN layers.
- `--x` : A string with format ('xmin:x_max:xnum').
- `--y` : A string with format ('ymin:ymax:ynum').
- `--xnorm` : The direction normalization ('filter' | 'layer' | 'weight').
- `--ynorm` : The direction normalization ('filter' | 'layer' | 'weight').
- `--xignore` : To ignore the direction corresponding to bias and BN parameters (fill the corresponding entries in the random vector with zeros) in the x-axis ("biasbn").
- `--yignore` : To ignore bias and BN parameters the y-axis ("biasbn").
- `--surf_file` : The customize the name of surface file, could be an existing file.
- `--proj_file` : The .h5 file contains projected optimization trajectory.
- `--loss_max` : Maximum value to show in 1D plot.
- `--vmax` : Maximum value to map in the plot.
- `--vmin` : Miminum value to map in the plot.
- `--vlevel` : Plot contours every vlevel.
- `--log` : Whether to use log scale for loss values.
- `--plot_format` : The save format of plotted matplotlib images (defaults to "png").
- `--model_folder` : Folders for models to be projected (defaults to work_dirs).
- `--prefix` : The prefix for the checkpint model for plotting the trajectory (defaults to "epoch").
- `--start_epoch` : The min index of epochs for plotting the trajectory.
- `--max_epoch` : The max number of epochs for plotting the trajectory.
- `--save_interval` : The interval to save models for plotting the trajectory.
- `--cfg-options` : Modifications to the configuration file, refer to [Tutorial 1: Learn about Configs](https://openmixup.readthedocs.io/en/latest/tutorials/0_config.html).

**Examples**：

1. Visualizing 1D linear interpolations. The 1D linear interpolation method evaluates the loss values along the direction between two minimizers of the same network loss function.

    ```shell
    bash tools/visualizations/dist_vis_loss.sh \
        configs/classification/cifar100/wa/resnet18_CE_bs100.py 1 ${CHECKPOINT} \
        --plot_mode surface --x=-1:1:51 --dir_type weights --xnorm filter --xignore biasbn
    ```
    ```{note}
    `--x=-1:1:51` sets the range and resolution for the plot. The x-coordinates in the plot will run from -1 to 1 (the minimizers are located at 0 and 1), and the loss value will be evaluated at 51 locations along this line.
    
    `--dir_type weights` indicates the direction has the same dimensions as the learned parameters, including bias and parameters in the BN layers.
    
    `--xnorm filter` normalizes the random direction at the filter level. Here, a "filter" refers to the parameters that produce a single feature map. For fully connected layers, a "filter" contains the weights that contribute to a single neuron.
    
    `--xignore biasbn` ignores the direction corresponding to bias and BN parameters (fill the corresponding entries in the random vector with zeros).
    ```
    <p align="center">
    <img src="https://user-images.githubusercontent.com/44519745/228991095-e0a63c1a-1d57-43e3-af2b-95c8840668ea.png" width=50% class="center">
    </p>

2. Visualizing 2D loss contours and 3D loss surfaces. To plot the loss landscape, we choose two random directions and normalize them in the same way as the 1D plotting.

    ```shell
    bash tools/visualizations/dist_vis_loss.sh \
        configs/classification/cifar100/wa/resnet18_CE_bs100.py 1 ${CHECKPOINT} \
        --plot_mode surface --x=-1:1:51 --y=-1:1:51 --dir_type weights \
        --xnorm filter --xignore biasbn --ynorm filter --yignore biasbn --vlevel 0.1
    ```
    | 2D contours | 3D surfaces |
    | :---: | :---: |
    | <div align=center><img src='https://user-images.githubusercontent.com/44519745/228991449-05f304ee-f66f-406c-90a7-cfe76ecf370b.png' height="auto" width="285" ></div> | <div align=center><img src='https://user-images.githubusercontent.com/44519745/228991893-22efdb41-c9b2-4cf3-8a76-33a626d36718.png' height="auto" width="250" ></div> |

3. Visualizing the loss trajectory in 2D loss contours. We plot the loss surfaces and the optimization trajectory in a 2D plot, which requires a list of models (saved in the path to `work_dirs`).

    ```shell
    bash tools/visualizations/dist_vis_loss.sh \
        configs/classification/cifar100/wa/resnet18_CE_bs100.py 1 ${CHECKPOINT} \
        --plot_mode surface+trajectory --x=-1:1:51 --y=-1:1:51 --dir_type weights \
        --xnorm filter --xignore biasbn --ynorm filter --yignore biasbn \
        --start_epoch 0 --max_epoch 200 --save_interval 10
    ```

## FAQs

- None

<p align="right">(<a href="#top">back to top</a>)</p>
