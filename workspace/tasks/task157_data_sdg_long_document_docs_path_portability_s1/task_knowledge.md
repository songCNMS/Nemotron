# Task Knowledge

<!-- METADATA:STATUS=Completed,TASK=task157_data_sdg_long_document_docs_path_portability_s1,ROLE=dev,SESSION=1 -->

- Long-document SDG examples should use `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` so docs do not steer users into named-user or cluster-specific storage.
- The task is documentation/comment/static-test only; manual vLLM and `--serve` examples must remain recognizable and keep the same CLI options.
- PR #266 was squash-merged to main at `2cb891846c6f86d8917cd6289070c687dfdd6f91` after independent PM gate and merged-main verification.
