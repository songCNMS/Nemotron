# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Scoped docs:
  `usage-cookbook/Nemotron-3-Super/README.md` and Super3 entries in
  `docs/deployment-guides.md`.
- Focused static test:
  `tests/docs/test_super3_cookbook_index_doc_links_revision_pins.py`.
- Required self-repo revision pin:
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Reject scoped mutable self-repo links matching
  `https://github.com/NVIDIA-NeMo/{Nemotron,nemotron}/{blob,tree}/main/usage-cookbook/Nemotron-3-Super...`.
- Preserve non-Super3 deployment guide links because they are out of task192
  scope.
- PR: https://github.com/songCNMS/Nemotron/pull/299.
- Closeout: PR #299 merged and verified on `main` at
  `c52776aabaada650b2435c2f9b7913f72f42e035`; tested/merged head was
  `027344a8c4c131105f3ab2b3ef544e94a2101ed4`.
