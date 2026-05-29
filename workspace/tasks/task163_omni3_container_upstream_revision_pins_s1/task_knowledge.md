# task163_omni3_container_upstream_revision_pins_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- PM-provided upstream pins:
  - Megatron-Bridge `nemotron_3_omni`:
    `648756cb99eed872d9e577243495840b9395a6f7`
  - Megatron-LM `nemotron_3_omni`:
    `bdecae692af213add7d8434e129ae482465d9731`
  - NeMo-RL `nano-v3-omni`:
    `98ba11c0a77e177a903cd3756570684437a08e8d`
- This task is static/offline only; the Dockerfiles were not built and no live
  upstream clone/fetch was run.
- Closeout: PR #270 merged to `main` at
  `83ffb47e2e7053ac189b9557011f3a9e6c9ea92c`; PM merged-main verification
  passed the focused static checks and Dockerfile revision-pin probe.
