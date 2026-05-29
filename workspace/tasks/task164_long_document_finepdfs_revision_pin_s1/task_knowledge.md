# Task Knowledge

<!-- METADATA:SESSION=2 -->

- FinePDFs seed loading must use repo `HuggingFaceFW/finepdfs` pinned to lowercase 40-character SHA `220bac3acbf07789502c621d2d33952f51ac7f86`.
- Task validation must remain offline/static; do not call `load_dataset`, download PDFs, or run the seed stage.
- PR #271 was merged and verified on main at `83119f9ca83a4978773f4702ef0a4b48c0c4fe94`; dev closeout did not perform live `load_dataset`, PDF downloads, data prep, serve, endpoints, W&B, cluster, deploy, artifact operations, train/eval, main push, or self-merge.
