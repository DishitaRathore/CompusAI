import json
from pathlib import Path

from datasets import ClassLabel, load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments
)


DATA_PATH = Path("data/intent_data.csv")
OUTPUT_DIR = Path("models/intent_classifier")

MODEL_NAME = "distilbert-base-uncased"


def main():
    print("Loading intent dataset...")

    dataset = load_dataset(
        "csv",
        data_files=str(DATA_PATH)
    )["train"]

    label_names = sorted(
        set(dataset["label"])
    )

    label2id = {
        label: index
        for index, label in enumerate(label_names)
    }

    id2label = {
        index: label
        for label, index in label2id.items()
    }

    def convert_label(example):
        example["label"] = label2id[
            example["label"]
        ]

        return example

    dataset = dataset.map(convert_label)

    dataset = dataset.cast_column(
        "label",
        ClassLabel(names=label_names)
    )

    dataset = dataset.train_test_split(
        test_size=0.2,
        seed=42,
        stratify_by_column="label"
    )
    

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    def tokenize_examples(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=128
        )

    tokenized_dataset = dataset.map(
        tokenize_examples,
        batched=True
    )

    tokenized_dataset = tokenized_dataset.remove_columns(
        ["text"]
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_names),
        id2label=id2label,
        label2id=label2id
    )

    data_collator = DataCollatorWithPadding(
        tokenizer=tokenizer
    )

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=8,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_steps=5,
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        processing_class=tokenizer,
        data_collator=data_collator
    )

    print("Starting transformer fine-tuning...")

    trainer.train()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    trainer.save_model(
        str(OUTPUT_DIR)
    )

    tokenizer.save_pretrained(
        str(OUTPUT_DIR)
    )

    label_path = OUTPUT_DIR / "labels.json"

    label_path.write_text(
        json.dumps(
            {
                "label2id": label2id,
                "id2label": id2label
            },
            indent=2
        ),
        encoding="utf-8"
    )

    print("Intent classifier trained successfully.")
    print(f"Model saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()