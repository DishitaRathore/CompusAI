import csv
import random
from collections import Counter
from pathlib import Path


random.seed(42)

OUTPUT_PATH = Path("data/intent_data.csv")
OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


EXAMPLES = {
    "attendance_query": [
        "What is my attendance?",
        "How many classes have I attended?",
        "Show my attendance percentage.",
        "Can you check my attendance?",
        "What is my attendance in Machine Learning?",
        "How many classes did I miss?",
        "Am I meeting the attendance requirement?",
        "Tell me my subject-wise attendance."
    ],

    "fee_query": [
        "What is my fee status?",
        "How much fee have I paid?",
        "How much fee is remaining?",
        "Show my pending fees.",
        "What is my total fee?",
        "Do I have any unpaid fees?",
        "Can you check my fee balance?",
        "Tell me about my education fees."
    ],

    "create_ticket": [
        "Create a support ticket.",
        "I want to raise a complaint.",
        "Open a ticket for me.",
        "Report an issue with my attendance.",
        "I need help from student support.",
        "My fee record is incorrect.",
        "Create a complaint about the ERP.",
        "I want to contact the help desk."
    ],

    "security_report": [
        "I received a phishing email.",
        "Someone sent me a suspicious link.",
        "I clicked a malicious link.",
        "I think my account was hacked.",
        "I received a suspicious message.",
        "I want to report unauthorized access.",
        "I downloaded a suspicious attachment.",
        "I think this message is a scam."
    ],

    "security_guidance": [
        "How can I protect my account?",
        "How do I create a strong password?",
        "Should I share my OTP?",
        "What is multi-factor authentication?",
        "How can I stay safe from phishing?",
        "What are basic cybersecurity practices?",
        "How should I protect my student account?",
        "How can I identify a suspicious email?"
    ],

    "policy_question": [
        "What is the attendance policy?",
        "What is the minimum attendance requirement?",
        "What are the student fee rules?",
        "Tell me about the college guidelines.",
        "What are the cybersecurity guidelines?",
        "What is the policy for incorrect attendance?",
        "What rules apply to student data?",
        "Explain the education portal policy."
    ],

    "chat_history": [
        "Show my previous messages.",
        "Can I see my conversation history?",
        "Load my past chats.",
        "What did I ask earlier?",
        "Show my previous chatbot conversation.",
        "I want to review my chat history."
    ],

    "unknown": [
        "What is the weather today?",
        "Tell me a joke.",
        "Who won the cricket match?",
        "Write a poem for me.",
        "What is the capital of France?",
        "Help me plan a vacation.",
        "Tell me about cooking recipes.",
        "What is the latest movie?"
    ]
}


def create_dataset():
    rows = []

    for label, examples in EXAMPLES.items():
        for example in examples:
            rows.append(
                {
                    "text": example,
                    "label": label
                }
            )

    random.shuffle(rows)

    with OUTPUT_PATH.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["text", "label"]
        )

        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(
        row["label"]
        for row in rows
    )

    print("Intent dataset created successfully.")
    print(f"Total examples: {len(rows)}")

    for label, count in sorted(counts.items()):
        print(f"{label}: {count}")


if __name__ == "__main__":
    create_dataset()