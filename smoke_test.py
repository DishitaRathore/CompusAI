import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

STUDENT_API_KEY = os.getenv("APP_API_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def call_api(
    path,
    method="GET",
    api_key=None,
    payload=None
):
    url = BASE_URL + path

    headers = {}

    if api_key:
        headers["X-API-Key"] = api_key

    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url=url,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_data = response.read().decode("utf-8")

            return response.status, json.loads(response_data)

    except HTTPError as error:
        error_data = error.read().decode("utf-8")

        return error.code, json.loads(error_data)


def run_tests():
    print("Running CampusFlow AI API tests...\n")

    status, data = call_api(
        path="/chat",
        method="POST",
        api_key=STUDENT_API_KEY,
        payload={
            "message": "What is my attendance?",
            "student_id": 1
        }
    )

    assert status == 200
    assert "answer" in data
    assert data["mode"] == "attendance"
    print("PASS: Student chat access")

    status, data = call_api(
        path="/chat-history/1",
        api_key=STUDENT_API_KEY
    )

    assert status == 200
    assert isinstance(data, list)
    print("PASS: Student chat history access")

    status, data = call_api(
        path="/security-events",
        api_key=STUDENT_API_KEY
    )

    assert status == 403
    print("PASS: Student blocked from security events")

    status, data = call_api(
        path="/security-events",
        api_key=ADMIN_API_KEY
    )

    assert status == 200
    assert isinstance(data, list)
    print("PASS: Admin security-event access")

    status, data = call_api(
        path="/audit-logs",
        api_key=ADMIN_API_KEY
    )

    assert status == 200
    assert isinstance(data, list)
    print("PASS: Admin audit-log access")

    print("\nAll API tests passed successfully.")


if __name__ == "__main__":
    run_tests()