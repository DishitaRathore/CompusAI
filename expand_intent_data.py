import csv
import random
from collections import Counter
from pathlib import Path


DATA_PATH = Path("data/intent_data.csv")


EXTRA_EXAMPLES = {
    "attendance_query": [
        "How is my attendance percentage calculated?",
        "Show attendance for all my subjects.",
        "How many classes have I missed this semester?",
        "Is my attendance above the required percentage?",
        "Show attendance for Database Systems.",
        "Do I have low attendance in any subject?",
        "Which subjects have attendance below 75 percent?",
        "How many lectures did I attend this month?",
        "Check my attendance record.",
        "What percentage of classes did I attend?",
        "Am I eligible based on my attendance?",
        "Give me an attendance summary.",
        "Tell me my attendance subject by subject.",
        "How many classes do I need to attend?",
    ],

    "fee_query": [
        "Show my complete fee details.",
        "How much money do I still owe?",
        "Is my semester fee fully paid?",
        "Tell me my outstanding balance.",
        "Show my fee payment history.",
        "When is my fee payment due?",
        "Do I have a pending fee payment?",
        "How much was my total tuition fee?",
        "Give me a summary of my fees.",
        "What amount is left to pay?",
        "Can you check my unpaid balance?",
        "Have I paid my current semester fees?",
        "Show the amount I have already paid.",
        "Tell me if any fees are overdue.",
    ],

    "create_ticket": [
        "Please open a support request.",
        "I need to submit a complaint.",
        "Create a help desk request for me.",
        "I want to report a problem with my student account.",
        "Please contact student support for me.",
        "Raise a ticket about my fee record.",
        "I need technical help with the ERP.",
        "Open a complaint about my attendance record.",
        "Submit a support request.",
        "Can you create a service ticket?",
        "I need assistance from the administration.",
        "Please report this issue to the help desk.",
        "I want to raise a student service request.",
        "Create a ticket because my data is incorrect.",
    ],

    "security_report": [
        "I received an email asking for my password.",
        "Someone is pretending to be the university.",
        "I clicked on a suspicious attachment.",
        "My account login looks unfamiliar.",
        "I received a fake fee payment message.",
        "There is unusual activity on my account.",
        "I want to report a cyber incident.",
        "A stranger asked me for my OTP.",
        "I entered my password on a suspicious website.",
        "I received a suspicious university notification.",
        "Someone may have accessed my account.",
        "I want to report a possible data breach.",
        "A message is asking me to verify my account urgently.",
        "I think my student credentials were stolen.",
    ],

    "security_guidance": [
        "How can I secure my student account?",
        "What should I do if I receive a phishing email?",
        "How can I recognize a fake login page?",
        "What makes a password secure?",
        "How does two-factor authentication protect me?",
        "Should I use the same password everywhere?",
        "How can I avoid cyber attacks?",
        "What should I do with a suspicious link?",
        "How can I protect my personal information?",
        "What are safe email practices?",
        "How often should I change my password?",
        "How can I keep my account secure?",
        "What should I do if someone asks for my OTP?",
        "How can students stay safe online?",
    ],

    "policy_question": [
        "Where can I find the attendance rules?",
        "What happens if my attendance is too low?",
        "Explain the fee payment policy.",
        "What are the rules for student complaints?",
        "Tell me the account security policy.",
        "What guidelines apply to student records?",
        "What is the policy for reporting incidents?",
        "Explain the rules for the education portal.",
        "What are the university data privacy rules?",
        "What is the minimum attendance percentage?",
        "Tell me the official cybersecurity rules.",
        "What are the rules for fee refunds?",
        "Explain the student support policy.",
        "Where can I read the college policies?",
    ],

    "chat_history": [
        "Show all my earlier questions.",
        "What messages have I sent before?",
        "Open my previous chat sessions.",
        "Can I review my earlier conversation?",
        "Show my recent chatbot activity.",
        "What did I ask the assistant yesterday?",
        "Display my conversation records.",
        "I want to see my old messages.",
        "Load the questions I asked earlier.",
        "Show my chatbot history.",
        "Can I review my previous requests?",
        "List my past conversations.",
        "Take me to my earlier chats.",
        "What have I discussed with the chatbot?",
    ],

    "unknown": [
        "Write a short story about a robot.",
        "What is the capital of Japan?",
        "Tell me a funny joke.",
        "How do I cook pasta?",
        "Who is the current cricket champion?",
        "Suggest a weekend travel plan.",
        "What movies are popular right now?",
        "Explain how to grow a plant.",
        "Tell me an interesting science fact.",
        "Write a poem about the ocean.",
        "What is the best way to learn guitar?",
        "Give me a healthy breakfast recipe.",
        "Tell me about famous landmarks.",
        "What will the weather be like?",
    ],
}


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {DATA_PATH}"
        )

    with DATA_PATH.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    existing = {
        (
            row["text"].strip().lower(),
            row["label"].strip()
        )
        for row in rows
    }

    added_count = 0

    for label, examples in EXTRA_EXAMPLES.items():
        for text in examples:
            key = (
                text.strip().lower(),
                label
            )

            if key not in existing:
                rows.append(
                    {
                        "text": text,
                        "label": label
                    }
                )
                existing.add(key)
                added_count += 1

    random.Random(42).shuffle(rows)

    with DATA_PATH.open(
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

    print("Intent dataset expanded successfully.")
    print(f"New examples added: {added_count}")
    print(f"Total examples: {len(rows)}")

    print("\nExamples per label:")
    for label, count in sorted(counts.items()):
        print(f"{label}: {count}")


if __name__ == "__main__":
    main()