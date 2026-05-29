# task168_lora_text2sql_bird_dataset_revision_pins_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- PM-provided metadata-only pins:
  - `xu3kev/BIRD-SQL-data-train` ->
    `9122256f9d14752ed80fb9b7d158e21d9f9261aa`
  - `meowterspace45/bird-sql-train-with-reasoning` ->
    `9e351e0057819f1b0917debb83c8e12f321157a4`
- The cookbook loader files live under a hyphenated path, so the focused tests
  use `ast.parse()` on file contents instead of importing modules.
- Tests must not call `load_dataset` or perform live HF downloads.
