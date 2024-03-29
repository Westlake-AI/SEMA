#!/usr/bin/env bash

set -e
set -x

PARTITION=$1
CFG=$2
PRETRAIN=$3
PY_ARGS=${@:4}
JOB_NAME="openmixup"
GPUS=4 # in the standard setting, GPUS=4
GPUS_PER_NODE=${GPUS_PER_NODE:-4}
CPUS_PER_TASK=${CPUS_PER_TASK:-5}
SRUN_ARGS=${SRUN_ARGS:-""}

WORK_DIR="$(echo ${CFG%.*} | sed -e "s/configs/work_dirs/g")/$(echo $PRETRAIN | rev | cut -d/ -f 1 | rev)"

# train
GLOG_vmodule=MemcachedClient=-1 \
srun -p ${PARTITION} \
    --job-name=${JOB_NAME} \
    --gres=gpu:${GPUS_PER_NODE} \
    --ntasks=${GPUS} \
    --ntasks-per-node=${GPUS_PER_NODE} \
    --cpus-per-task=${CPUS_PER_TASK} \
    --kill-on-bad-exit=1 \
    ${SRUN_ARGS} \
    python -u tools/train.py \
        $CFG \
        --pretrained $PRETRAIN \
        --work_dir $WORK_DIR --seed 0 --launcher="slurm" ${PY_ARGS}
