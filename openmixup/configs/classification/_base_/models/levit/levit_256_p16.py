# model settings
model = dict(
    type='MixUpClassification',
    pretrained=None,
    alpha=[0.8, 1.0,],
    mix_mode=["mixup", "cutmix",],
    mix_args=dict(),
    backbone=dict(
        type='LeViT',
        arch='256',
        img_size=224,
        patch_size=16,
        drop_path_rate=0,
        attn_ratio=2,
        mlp_ratio=2,
        out_indices=(2,)),
    head=dict(
        type='LeViTClsHead',
        loss=dict(type='LabelSmoothLoss',
            label_smooth_val=0.1, num_classes=1000, mode='original', loss_weight=1.0),
        distillation=False, deploy=False,
        with_avg_pool=True,
        in_channels=512, num_classes=1000),
    init_cfg=[
        dict(type='TruncNormal', layer='Linear', std=0.02, bias=0.),
        dict(type='Constant', layer=['LayerNorm', 'BatchNorm'], val=1., bias=0.)
    ],
)
