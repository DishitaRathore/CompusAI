from tools import sanitize_sensitive_text


def main():
    original = (
        "Contact alice@example.com or "
        "+91 9876543210. "
        "password=demo-password "
        "api_key=demo-api-key"
    )

    masked = sanitize_sensitive_text(
        original
    )

    assert "alice@example.com" not in masked
    assert "9876543210" not in masked
    assert "demo-password" not in masked
    assert "demo-api-key" not in masked

    assert "[EMAIL_REDACTED]" in masked
    assert "[PHONE_REDACTED]" in masked
    assert "[REDACTED]" in masked

    print("Sensitive-data masking test passed.")
    print(masked)


if __name__ == "__main__":
    main()