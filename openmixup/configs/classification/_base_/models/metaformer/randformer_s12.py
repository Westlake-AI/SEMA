# model settings
model = dict(
    type='MixUpClassification',
    pretrained=None,
    alpha=[0.8, 1.0,],
    mix_mode=["mixup", "cutmix",],
    mix_args=dict(),
    backbone=dict(
        type='MetaFormer',
        arch='randformer_s12',
        drop_path_rate=0.1,
    ),
    head=dict(
        type='MetaFormerClsHead',
        loss=dict(type='LabelSmoothLoss',
            label_smooth_val=0.1, num_classes=1000, mode='original', loss_weight=1.0),
        with_avg_pool=True,
        head_dropout=0.,
        in_channels=512, num_classes=1000),
    init_cfg=[
        dict(type='TruncNormal', layer=['Conv2d', 'Linear'], std=0.02, bias=0.),
        dict(type='Constant', layer=['LayerNorm', 'GroupNorm'], val=1., bias=0.)
    ],
)
