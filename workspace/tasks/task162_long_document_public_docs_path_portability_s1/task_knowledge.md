# Task Knowledge

<!-- METADATA:STATUS=Working,TASK=task162_long_document_public_docs_path_portability_s1,ROLE=dev,SESSION=1 -->

- Public long-document SDG docs should use `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` examples and avoid concrete cluster/user storage paths.
- The task is docs/static-test only; manual endpoint and `--serve` examples must remain recognizable with the same CLI options.
