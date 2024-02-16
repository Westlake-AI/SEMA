# model settings
model = dict(
    type='Classification',
    pretrained=None,
    backbone=dict(
        type='Res2Net',
        depth=50,
        scales=2,
        base_width=48,
        deep_stem=False,
        avg_down=False,
        out_indices=(3,)
    ),
    head=dict(
        type='ClsHead',
        loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        with_avg_pool=True, in_channels=2048, num_classes=1000)
)
