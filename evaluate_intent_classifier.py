import json
from pathlib import Path

import numpy as np
from datasets import ClassLabel, load_dataset
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer
)


DATA_PATH = Path("data/intent_data.csv")
MODEL_DIR = Path("models/intent_classifier")


def main():
    labels_data = json.loads(
        (MODEL_DIR / "labels.json").read_text(
            encoding="utf-8"
        )
    )

    label2id = labels_data["label2id"]
    id2label = {
        int(key): value
        for key, value in labels_data["id2label"].items()
    }

    label_names = [
        id2label[index]
        for index in range(len(id2label))
    ]

    dataset = load_dataset(
        "csv",
        data_files=str(DATA_PATH)
    )["train"]

    def convert_label(example):
        example["label"] = label2id[
            example["label"]
        ]
        return example

    dataset = dataset.map(convert_label)

    dataset = dataset.cast_column(
        "label",
        ClassLabel(names=list(label2id.keys()))
    )

    dataset = dataset.train_test_split(
        test_size=0.2,
        seed=42,
        stratify_by_column="label"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL_DIR)
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
        str(MODEL_DIR)
    )

    data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer
    )

    trainer = Trainer(model=model, data_collator=data_collator)

    result = trainer.predict(
        tokenized_dataset["test"]
    )

    predictions = np.argmax(
        result.predictions,
        axis=-1
    )

    actual_labels = np.array(
        tokenized_dataset["test"]["label"]
    )

    print(
        f"Accuracy: "
        f"{accuracy_score(actual_labels, predictions):.4f}\n"
    )

    print("Classification report:")
    print(
        classification_report(
            actual_labels,
            predictions,
            labels=list(range(len(label_names))),
            target_names=label_names,
            zero_division=0
        )
    )

    print("Confusion matrix:")
    print(
        confusion_matrix(
            actual_labels,
            predictions
        )
    )


if __name__ == "__main__":
    main()