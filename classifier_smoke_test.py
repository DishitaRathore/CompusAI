import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("APP_API_KEY")
STUDENT_ID = 1001


TEST_CASES = [
    ("What is my attendance?", "attendance"),
    ("How much fee is remaining?", "fees"),
    ("Create a support ticket for my ERP issue.", "ticket"),
    ("I received a phishing email.", "security_event"),
    ("What is the attendance policy?", "rag_llm"),
    ("Show my previous messages.", "chat_history"),
    ("Tell me a joke.", "fallback"),
]


def call_chat(message):
    payload = json.dumps(
        {
            "message": message,
            "student_id": STUDENT_ID
        }
    ).encode("utf-8")

    request = Request(
        url=f"{BASE_URL}/chat",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            return response.status, json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        body = error.read().decode("utf-8")
        raise AssertionError(
            f"HTTP {error.code}: {body}"
        )


def main():
    if not API_KEY:
        raise RuntimeError(
            "APP_API_KEY was not found in .env"
        )

    print("Testing classifier-driven chatbot routing...\n")

    for message, expected_mode in TEST_CASES:
        status, data = call_chat(message)

        actual_mode = data.get("mode")

        if status != 200:
            raise AssertionError(
                f"Request failed for: {message}"
            )

        if actual_mode != expected_mode:
            raise AssertionError(
                f"{message}\n"
                f"Expected: {expected_mode}\n"
                f"Received: {actual_mode}\n"
                f"Response: {data}"
            )

        print(
            f"PASS: {message} "
            f"-> {actual_mode}"
        )

    print("\nAll classifier routing tests passed.")


if __name__ == "__main__":
    main()