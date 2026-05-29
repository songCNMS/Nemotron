# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Cookbook MMPR-Tiny downloads must use repo `OpenGVLab/MMPR-Tiny` pinned to lowercase 40-character SHA `eb493212c9614b69ca49cd6e66719413c514459b`.
- The converter must not use `ZipFile.extractall`; synthetic zip tests should mock `hf_hub_download` and avoid live HF/MMPR data access.
- PR #274 was merged and verified on main at `6328c018a86da7448e11a03bc1c71afc38e067f2`; dev closeout did not perform live HF/MMPR download, real conversion, train/eval, endpoint, W&B, cluster, deploy, artifact operations, main/master push, or self-merge.
