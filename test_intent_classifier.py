from intent_classifier import classify_intent


questions = [
    "What is my attendance?",
    "How much fee is remaining?",
    "I received a phishing email.",
    "How can I protect my account?",
    "Show my previous messages.",
    "What is the weather today?"
]


for question in questions:
    intent, confidence = classify_intent(question)

    print(f"\nQuestion: {question}")
    print(f"Intent: {intent}")
    print(f"Confidence: {confidence:.2f}")