# Task Knowledge

- Long-document SDG examples should use `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` so docs do not steer users into named-user or cluster-specific storage.
- The task is documentation/comment/static-test only; manual vLLM and `--serve` examples must remain recognizable and keep the same CLI options.
