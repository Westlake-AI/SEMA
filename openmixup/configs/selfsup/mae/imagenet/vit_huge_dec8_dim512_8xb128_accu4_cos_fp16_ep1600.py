_base_ = [
    '../../_base_/models/mae/vit_huge.py',
    '../../_base_/datasets/imagenet/mae_sz224_bs256.py',
    '../../_base_/default_runtime.py',
]

# dataset
data = dict(imgs_per_gpu=128, workers_per_gpu=8)

# interval for accumulate gradient
update_interval = 4  # total: 8 x bs128 x 4 accumulates = bs4096

# additional hooks
custom_hooks = [
    dict(type='SAVEHook',
        save_interval=1252 * 20,  # plot every 20 ep
        iter_per_epoch=1252),
]

# optimizer
optimizer = dict(
    type='AdamW',
    lr=1.5e-4 * 4096 / 256,  # bs4096
    betas=(0.9, 0.95), weight_decay=0.05,
    paramwise_options={
        '(bn|ln|gn)(\d+)?.(weight|bias)': dict(weight_decay=0.),
        'norm': dict(weight_decay=0.),
        'bias': dict(weight_decay=0.),
        'pos_embed': dict(weight_decay=0.),
        'mask_token': dict(weight_decay=0.),
        'cls_token': dict(weight_decay=0.)
    })

# fp16
use_fp16 = True
fp16 = dict(type='mmcv', loss_scale='dynamic')
# optimizer args
optimizer_config = dict(update_interval=update_interval, grad_clip=None)

# lr scheduler
lr_config = dict(
    policy='StepFixCosineAnnealing',
    by_epoch=False, min_lr=0.,
    warmup='linear',
    warmup_iters=40, warmup_by_epoch=True,
    warmup_ratio=1e-4,
)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=1600)
