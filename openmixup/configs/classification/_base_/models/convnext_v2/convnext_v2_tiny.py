# model settings
model = dict(
    type='MixUpClassification',
    pretrained=None,
    alpha=[0.8, 1.0,],
    mix_mode=["mixup", "cutmix",],
    mix_args=dict(),
    backbone=dict(
        type='ConvNeXt',
        arch='tiny',
        drop_path_rate=0.2,
        layer_scale_init_value=0.,
        use_grn=True,
    ),
    head=dict(
        type='ClsMixupHead',
        loss=dict(type='LabelSmoothLoss',
            label_smooth_val=0.2, num_classes=1000, mode='original', loss_weight=1.0),
        with_avg_pool=False,
        in_channels=768, num_classes=1000),
    init_cfg=[
        dict(type='TruncNormal', layer=['Conv2d', 'Linear'], std=0.02, bias=0.),
        dict(type='Constant', layer='LayerNorm', val=1., bias=0.)
    ],
)
