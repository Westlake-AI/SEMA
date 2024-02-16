# model settings
model = dict(
    type='MAE',
    backbone=dict(
        type='MAEViT',
        arch='small', patch_size=16, mask_ratio=0.75),
    neck=dict(
        type='MAEPretrainDecoder',
        patch_size=16,
        in_chans=3,
        embed_dim=384,
        decoder_embed_dim=192,
        decoder_depth=6,  # 3/4 * eocoder depth
        decoder_num_heads=16,
        mlp_ratio=4.,
    ),
    head=dict(type='MAEPretrainHead', norm_pix=True, patch_size=16)
)
