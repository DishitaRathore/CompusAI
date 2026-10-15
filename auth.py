import json
import os
import secrets

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status


load_dotenv()

STUDENT_API_KEY = os.getenv("APP_API_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def load_student_api_keys():
    raw_value = os.getenv(
        "STUDENT_API_KEYS_JSON",
        ""
    )

    student_keys = {}

    if raw_value:
        try:
            parsed_value = json.loads(raw_value)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "STUDENT_API_KEYS_JSON is not valid JSON."
            ) from error

        if not isinstance(parsed_value, dict):
            raise RuntimeError(
                "STUDENT_API_KEYS_JSON must be a JSON object."
            )

        student_keys = {
            str(student_id): str(api_key)
            for student_id, api_key in parsed_value.items()
        }

    # Preserve the existing student key for student 1001.
    if STUDENT_API_KEY:
        student_keys.setdefault(
            "1001",
            STUDENT_API_KEY
        )

    return student_keys


STUDENT_API_KEYS = load_student_api_keys()


def get_current_user(
    x_api_key: str = Header(default="")
):
    if (
        ADMIN_API_KEY
        and secrets.compare_digest(
            x_api_key,
            ADMIN_API_KEY
        )
    ):
        return {
            "role": "admin",
            "student_id": None
        }

    for student_id, api_key in STUDENT_API_KEYS.items():
        if (
            api_key
            and secrets.compare_digest(
                x_api_key,
                api_key
            )
        ):
            return {
                "role": "student",
                "student_id": int(student_id)
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key"
    )


def get_user_role(
    x_api_key: str = Header(default="")
) -> str:
    user = get_current_user(
        x_api_key=x_api_key
    )

    return user["role"]


def verify_api_key(
    x_api_key: str = Header(default="")
):
    get_current_user(
        x_api_key=x_api_key
    )

    return True


def require_admin(
    x_api_key: str = Header(default="")
):
    user = get_current_user(
        x_api_key=x_api_key
    )

    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    return True