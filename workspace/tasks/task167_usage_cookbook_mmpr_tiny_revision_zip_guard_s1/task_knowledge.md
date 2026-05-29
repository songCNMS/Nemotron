# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Cookbook MMPR-Tiny downloads must use repo `OpenGVLab/MMPR-Tiny` pinned to lowercase 40-character SHA `eb493212c9614b69ca49cd6e66719413c514459b`.
- The converter must not use `ZipFile.extractall`; synthetic zip tests should mock `hf_hub_download` and avoid live HF/MMPR data access.
