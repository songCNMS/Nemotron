# Qwen Training Loss Reasoning Content Check - Session 84

## Question

Is the training loss applied only to final answers, or does it include the thinking / step-by-step solution content?

## Answer

For the current Qwen V3/V4/V5/V6 SFT artifacts, visible step-by-step solution content is in the training loss. It is not only supervising final boxed answers.

Important distinction:

- Hidden Qwen-style `reasoning_content` / `<think>` blocks are not present in the current M1 math JSONLs.
- The math "thinking" that exists in these datasets is visible assistant `content`: derivations, equations, explanations, and final boxed answers.
- The data-prep loss mask marks the whole assistant chunk as supervised, so visible derivations and final answers both enter loss.

## Code Path

The relevant pipeline is:

1. M0 math converters write source full solutions into `extra_env_info.reference_solution`.
2. M1 `assistant_for_reasoning` builds an assistant message whose `content` is the full reference solution, with `Final answer: \boxed{...}` appended only when the solution lacks a boxed final.
3. SFT data prep renders JSONL `messages` with the Qwen tokenizer template.
4. `chat_sft_shard_core._tokenize_chunks_with_mask` sets loss mask `1` for every assistant chunk token and `0` for system/user/tool chunks.
5. Packing shifts the mask to Megatron-Bridge label semantics, so tokens inside the assistant solution are still the supervised labels.

## Raw Tokenization Evidence

I sampled one full-solution math row from each current sidecar and reran the actual helper path:

`create_masked_messages -> split_system_user_chunks -> _tokenize_chunks_with_mask`

| Dataset | Assistant chars | Assistant tokens | Assistant raw loss tokens | Raw assistant mask all ones | Reasoning before final/box |
|---|---:|---:|---:|---:|---|
| V3 verified | 1513 | 664 | 664 | yes | yes |
| V4 hard | 1513 | 664 | 664 | yes | yes |
| V5 hard | 1513 | 664 | 664 | yes | yes |
| V6 hard | 1394 | 429 | 429 | yes | yes |
| V6 broad | 1800 | 562 | 562 | yes | yes |

Example V5 supervised assistant head begins with the derivation:

```text
(1) Since y=4cos^2x+4sqrt(3)sin x cos x-2 ...
thus, its smallest positive period ...
```

This is before the first boxed answer and has mask `1`.

## Packed Parquet Evidence

I also checked actual packed train parquet rows and reconstructed supervised label tokens using the shifted mask rule: `loss_mask[j]` gates label token `input_ids[j+1]`.

| Run | Packed row / segment | Label loss tokens | Supervised chars before first `\boxed` | Reasoning before box |
|---|---|---:|---:|---|
| V3 | `shard_000000.parquet`, row 0, segment 0 | 1088 | 3483 | yes |
| V4 | `shard_000000.parquet`, row 0, segment 0 | 1086 | 2585 | yes |
| V5 | `shard_000000.parquet`, row 0, segment 0 | 517 | 328 | yes |
| V6 | `shard_000000.parquet`, row 0, segment 0 | 974 | 759 | yes |

The supervised label text starts with derivations such as:

```text
1. **Base Case**:

We start by considering the base case ...
```

and:

```text
Given the radius of the moving circle C is r, we have ...
```

These are not final-answer-only labels.

## What This Means

The current failure mode is not "only final answers are in loss." The model is trained on visible solution traces.

The stronger issue is that the visible traces being supervised are often:

- much shorter than original Qwen's successful AIME/HMMT responses,
- sometimes low-quality or shortcut-like,
- sometimes malformed around final boxing,
- limited by `pack_size=4096` / training `seq_length=4096`,
- not verified by a proof-quality checker.

So the model can learn to produce short, parser-readable but wrong reasoning, because that entire visible assistant solution style is under loss.

## Practical Conclusion

Keep the Qwen tokenizer template and assistant loss-mask contract. The fix should be in data quality and sequence-length strategy:

- add longer verified hard-math solution traces,
- filter malformed and shortcut reasoning more aggressively,
- add correctness or verifier consistency checks for sidecar rows,
- use a hard-math pilot gate that inspects parsed-correct ratio and average completion length,
- add a regression test that decodes a packed math row and asserts pre-final solution tokens are supervised.
