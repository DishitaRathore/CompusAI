import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
STUDENT_KEY = os.getenv("APP_API_KEY")


def main():
    rate_limit_received = False

    for request_number in range(1, 32):
        request = Request(
            url=f"{BASE_URL}/chat-history/1001",
            headers={
                "X-API-Key": STUDENT_KEY
            },
            method="GET"
        )

        try:
            with urlopen(
                request,
                timeout=30
            ) as response:
                status = response.status

        except HTTPError as error:
            status = error.code

            if status == 429:
                retry_after = error.headers.get(
                    "Retry-After"
                )

                print(
                    f"PASS: Request {request_number} "
                    f"was rate-limited"
                )
                print(
                    f"Retry-After: {retry_after} seconds"
                )

                rate_limit_received = True
                break

        if status != 200:
            raise AssertionError(
                f"Unexpected status: {status}"
            )

        print(
            f"Request {request_number}: 200 OK"
        )

    if not rate_limit_received:
        raise AssertionError(
            "Expected HTTP 429 was not received."
        )

    print("\nRate-limit test passed.")


if __name__ == "__main__":
    main()