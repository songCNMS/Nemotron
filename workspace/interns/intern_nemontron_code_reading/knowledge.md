# intern_nemontron_code_reading - personal knowledge base

<!-- METADATA:SESSION=6 -->

---

## Knowledge entries

### Task005 Qwen full-loop validation

For M1 Agentic SFT on `NemTron`, use `/root/nemotron_session5_venv/bin/python` with `PYTHONPATH=$PWD/src`, Qwen3-4B-Instruct-2507 model/tokenizer at `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`, and pretrained Bridge checkpoint `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`. Eval-only runs still need nonzero scheduler steps; `train.train_iters=1 scheduler.lr_decay_iters=1 scheduler.lr_warmup_iters=0 train.skip_train=true` is the stable override.
