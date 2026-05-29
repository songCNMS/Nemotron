# intern_nem_dev_2 - 个人知识库

<!-- METADATA:SESSION=0 -->

---

## 知识条目

- benchmark alignment source manifest guards: validate raw slash-separated
  repo-relative components before `Path.resolve()`, then use
  `resolve(strict=True)` plus `relative_to(REPO_ROOT.resolve(strict=True))` to
  reject symlink escapes and directories.
