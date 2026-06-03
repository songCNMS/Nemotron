# task327_qwen_all_sft_large_source_materialize_decontam_s1 - task knowledge

1. Task322/#388 accepted two bounded sources and excluded 10 large selected HF
   files due the 1GB materialization threshold.
2. The 10 excluded files total 242,773,079,314 selected bytes and currently
   block a full all-eligible-SFT packed-data contract.
3. Task327 is no-training/no-packing raw evidence only. It may not authorize
   optimizer launch, benchmark eval, export, endpoint, or promotion.
4. Any source lacking row counts, checksums, row manifests, decontam proof, or
   split exposure must remain blocked/excluded for later packing.
