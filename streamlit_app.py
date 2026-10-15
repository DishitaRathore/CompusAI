import os
from typing import Any

import requests
import streamlit as st


API_URL = os.getenv(
    "CAMPUSFLOW_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="CampusFlow AI",
    page_icon="🎓",
    layout="wide"
)


def api_headers(api_key: str) -> dict:
    return {
        "X-API-Key": api_key
    }


def show_api_error(response: requests.Response) -> None:
    try:
        detail = response.json()
    except ValueError:
        detail = response.text

    st.error(f"API error {response.status_code}: {detail}")


def get_json(
    path: str,
    api_key: str,
    timeout: int = 30
) -> Any:
    try:
        response = requests.get(
            f"{API_URL}{path}",
            headers=api_headers(api_key),
            timeout=timeout
        )

        if not response.ok:
            show_api_error(response)
            return None

        return response.json()

    except requests.RequestException as error:
        st.error(f"Could not connect to FastAPI: {error}")
        return None


def send_chat(
    student_id: int,
    message: str,
    api_key: str
) -> Any:
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "student_id": student_id,
                "message": message
            },
            headers=api_headers(api_key),
            timeout=120
        )

        if not response.ok:
            show_api_error(response)
            return None

        return response.json()

    except requests.RequestException as error:
        st.error(f"Could not connect to FastAPI: {error}")
        return None


def display_history(data: Any) -> None:
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                role = item.get("role", "assistant")
                content = item.get("content", str(item))

                chat_role = "user" if role == "user" else "assistant"

                with st.chat_message(chat_role):
                    st.write(content)
            else:
                st.write(item)
    else:
        st.json(data)


st.title("🎓 CampusFlow AI")
st.caption("Student support and cybersecurity assistant")

with st.sidebar:
    st.header("Settings")

    mode = st.radio(
        "Select mode",
        ["Student", "Administrator"]
    )

    api_url_input = st.text_input(
        "FastAPI URL",
        value=API_URL
    )

    if api_url_input:
        API_URL = api_url_input.rstrip("/")

    if mode == "Student":
        student_id = st.number_input(
            "Student ID",
            min_value=1,
            value=1001,
            step=1
        )

        api_key = st.text_input(
            "Student API key",
            value=os.getenv("APP_API_KEY", ""),
            type="password"
        )
    else:
        student_id = st.number_input(
            "Student ID to inspect",
            min_value=1,
            value=1001,
            step=1
        )

        api_key = st.text_input(
            "Admin API key",
            value=os.getenv("ADMIN_API_KEY", ""),
            type="password"
        )


if mode == "Student":
    st.header("Student Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear current chat"):
        st.session_state.messages = []
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input(
        "Ask about attendance, fees, policies, or support..."
    )

    if user_message:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):
            if not api_key:
                st.error("Enter your student API key in the sidebar.")
            else:
                result = send_chat(
                    int(student_id),
                    user_message,
                    api_key
                )

                if result:
                    answer = result.get(
                        "answer",
                        "No answer returned."
                    )

                    st.write(answer)

                    mode_value = result.get("mode")
                    if mode_value:
                        st.caption(f"Response mode: {mode_value}")

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

    st.divider()

    if st.button("Load my chat history"):
        if not api_key:
            st.error("Enter your student API key in the sidebar.")
        else:
            history = get_json(
                f"/chat-history/{int(student_id)}",
                api_key
            )

            if history is not None:
                st.subheader("Chat history")
                display_history(history)


else:
    st.header("Administrator Dashboard")

    if not api_key:
        st.warning("Enter the administrator API key in the sidebar.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Load security events"):
            if api_key:
                events = get_json(
                    "/security-events",
                    api_key
                )

                if events is not None:
                    st.subheader("Security events")
                    st.json(events)

    with col2:
        if st.button("Load audit logs"):
            if api_key:
                logs = get_json(
                    "/audit-logs",
                    api_key
                )

                if logs is not None:
                    st.subheader("Audit logs")
                    st.json(logs)

    if st.button("Load student chat history"):
        if api_key:
            history = get_json(
                f"/chat-history/{int(student_id)}",
                api_key
            )

            if history is not None:
                st.subheader("Student chat history")
                display_history(history)