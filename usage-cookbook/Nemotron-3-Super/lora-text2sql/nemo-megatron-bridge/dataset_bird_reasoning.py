from base_sft_dataset import BaseSFTDataset
from datasets import Dataset, load_dataset

BIRD_REASONING_DATASET_REPO = "meowterspace45/bird-sql-train-with-reasoning"
BIRD_REASONING_DATASET_REVISION = "9e351e0057819f1b0917debb83c8e12f321157a4"

USER_MESSAGE_TEMPLATE = """
{schema}

{question}
{evidence}
"""


class DatasetBIRDReasoning(BaseSFTDataset):

    def _apply_chat_template(self, row, idx):

        schema = row["schema"]
        question = row["question"]
        evidence = row["evidence"]
        sql = row["SQL"]
        reasoning = row["reasoning_trace"].strip()

        user_message = USER_MESSAGE_TEMPLATE.format(
            schema=schema,
            question=question,
            evidence=evidence,
        ).strip()
        assistant_response = f"{reasoning}\n</think>\n\n{sql}".strip()
        prompt = self._get_prompt_with_chat_template_applied(
            system_message="",
            user_message=user_message,
            enable_reasoning=True,
        )
        completion = assistant_response + self.eot_marker
        return {
            "input": prompt,
            "output": completion,
        }

    def _load_dataset(self) -> Dataset:
        return load_dataset(
            BIRD_REASONING_DATASET_REPO,
            split="train",
            revision=BIRD_REASONING_DATASET_REVISION,
        )

    def _prepare_dataset(self, dataset: Dataset):
        dataset = dataset.map(
            self._apply_chat_template,
            with_indices=True,
            load_from_cache_file=False,
            num_proc=self.num_workers,
        )

        return dataset
