import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

STUDENT_KEY = os.getenv("APP_API_KEY")
ADMIN_KEY = os.getenv("ADMIN_API_KEY")


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
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)

    except HTTPError as error:
        return error.code, json.loads(
            error.read().decode("utf-8")
        )


def check(label, status, expected):
    if status != expected:
        raise AssertionError(
            f"{label}: expected {expected}, got {status}"
        )

    print(f"PASS: {label}")


def main():
    status, _ = call_api(
        path="/chat",
        api_key=STUDENT_KEY,
        method="POST",
        payload={
            "message": "What is my attendance?",
            "student_id": 1001
        }
    )
    check(
        "Student can access own chat",
        status,
        200
    )

    status, _ = call_api(
        path="/chat",
        api_key=STUDENT_KEY,
        method="POST",
        payload={
            "message": "What is my attendance?",
            "student_id": 1002
        }
    )
    check(
        "Student blocked from another student's chat",
        status,
        403
    )

    status, _ = call_api(
        path="/chat-history/1001",
        api_key=STUDENT_KEY
    )
    check(
        "Student can access own history",
        status,
        200
    )

    status, _ = call_api(
        path="/chat-history/1002",
        api_key=STUDENT_KEY
    )
    check(
        "Student blocked from another student's history",
        status,
        403
    )

    status, _ = call_api(
        path="/chat",
        api_key=ADMIN_KEY,
        method="POST",
        payload={
            "message": "What is my attendance?",
            "student_id": 1002
        }
    )
    check(
        "Admin can access another student's chat",
        status,
        200
    )

    print("\nAll authorization tests passed.")


if __name__ == "__main__":
    main()