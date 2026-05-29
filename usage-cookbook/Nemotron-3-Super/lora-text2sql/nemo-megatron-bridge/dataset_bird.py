from base_sft_dataset import BaseSFTDataset
from datasets import Dataset, load_dataset

BIRD_SQL_DATASET_REPO = "xu3kev/BIRD-SQL-data-train"
BIRD_SQL_DATASET_REVISION = "9122256f9d14752ed80fb9b7d158e21d9f9261aa"

USER_MESSAGE_TEMPLATE = """
{schema}

{question}
{evidence}
"""


class DatasetBIRD(BaseSFTDataset):

    def _apply_chat_template(self, row, idx):
        schema = row["schema"]
        question = row["question"]
        evidence = row["evidence"]
        sql = row["SQL"]

        user_message = USER_MESSAGE_TEMPLATE.format(
            schema=schema,
            question=question,
            evidence=evidence,
        ).strip()
        assistant_response = f"{sql}".strip()

        prompt = self._get_prompt_with_chat_template_applied(
            system_message="",
            user_message=user_message,
            enable_reasoning=False,
        )
        completion = assistant_response + self.eot_marker

        return {
            "input": prompt,
            "output": completion,
        }

    def _load_dataset(self) -> Dataset:
        return load_dataset(
            BIRD_SQL_DATASET_REPO,
            split="train",
            revision=BIRD_SQL_DATASET_REVISION,
        )

    def _prepare_dataset(self, dataset: Dataset):
        dataset = dataset.map(
            self._apply_chat_template,
            with_indices=True,
            load_from_cache_file=False,
            num_proc=self.num_workers,
        )

        return dataset
