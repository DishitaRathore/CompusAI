import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
STUDENT_KEY = os.getenv("APP_API_KEY")
ADMIN_KEY = os.getenv("ADMIN_API_KEY")

EMAIL = "alice@example.com"
PHONE = "+91 9876543210"


def call_api(
    path,
    api_key,
    method="GET",
    payload=None
):
    data = None
    headers = {
        "X-API-Key": api_key
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url=BASE_URL + path,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=120) as response:
            return response.status, json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        return error.code, json.loads(
            error.read().decode("utf-8")
        )


def main():
    message = (
        f"I received a phishing email from {EMAIL}. "
        f"Call me at {PHONE}."
    )

    status, data = call_api(
        path="/chat",
        api_key=STUDENT_KEY,
        method="POST",
        payload={
            "message": message,
            "student_id": 1001
        }
    )

    if status != 200 or data.get("mode") != "security_event":
        raise AssertionError(
            f"Security report failed: {status}, {data}"
        )

    print("PASS: Security report created")

    for endpoint in (
        "/security-events",
        "/audit-logs"
    ):
        status, data = call_api(
            path=endpoint,
            api_key=ADMIN_KEY
        )

        if status != 200:
            raise AssertionError(
                f"{endpoint} failed with {status}"
            )

        response_text = json.dumps(data)

        if EMAIL in response_text:
            raise AssertionError(
                f"Raw email appeared in {endpoint}"
            )

        if "9876543210" in response_text:
            raise AssertionError(
                f"Raw phone number appeared in {endpoint}"
            )

        print(
            f"PASS: Sensitive data masked in {endpoint}"
        )

    print("\nPII masking API test passed.")


if __name__ == "__main__":
    main()