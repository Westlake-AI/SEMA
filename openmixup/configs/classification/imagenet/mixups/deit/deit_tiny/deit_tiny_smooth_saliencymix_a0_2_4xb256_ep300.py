_base_ = "../deit_tiny_smooth_mix_4xb256.py"

# model settings
model = dict(
    alpha=0.2,
    mix_mode="saliencymix",
)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=300)
