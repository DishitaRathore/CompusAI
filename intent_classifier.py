import json
from pathlib import Path
from typing import Dict, Tuple

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_DIR / "models" / "intent_classifier"


if not MODEL_DIR.exists():
    raise FileNotFoundError(
        f"Classifier model not found at: {MODEL_DIR}"
    )


tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_DIR)
)


if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")


model.to(DEVICE)
model.eval()


def _load_id2label() -> Dict[int, str]:
    labels_path = MODEL_DIR / "labels.json"

    if labels_path.exists():
        with labels_path.open("r", encoding="utf-8") as file:
            labels_data = json.load(file)

        if isinstance(labels_data, dict):
            raw_id2label = labels_data.get("id2label")

            if raw_id2label:
                return {
                    int(key): str(value)
                    for key, value in raw_id2label.items()
                }

            raw_label2id = labels_data.get("label2id")

            if raw_label2id:
                return {
                    int(value): str(key)
                    for key, value in raw_label2id.items()
                }

        if isinstance(labels_data, list):
            return {
                index: str(label)
                for index, label in enumerate(labels_data)
            }

    model_id2label = getattr(model.config, "id2label", {})

    return {
        int(key): str(value)
        for key, value in model_id2label.items()
    }


ID2LABEL = _load_id2label()


def classify_intent(
    text: str,
    threshold: float = 0.55
) -> Tuple[str, float]:
    """
    Classify a user message.

    Returns:
        A tuple containing:
        - predicted intent label
        - confidence score
    """

    if not text or not text.strip():
        return "unknown", 0.0

    encoded_text = tokenizer(
        text.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    encoded_text = {
        key: value.to(DEVICE)
        for key, value in encoded_text.items()
    }

    with torch.inference_mode():
        output = model(**encoded_text)
        probabilities = torch.softmax(
            output.logits,
            dim=-1
        )[0]

    predicted_id = int(torch.argmax(probabilities).item())
    confidence = float(probabilities[predicted_id].item())

    label = ID2LABEL.get(
        predicted_id,
        f"LABEL_{predicted_id}"
    )

    if confidence < threshold:
        label = "unknown"

    return label, confidence