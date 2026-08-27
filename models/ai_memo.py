import os
import json
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from prompts.memo_prompt import MEMO_SYSTEM_PROMPT

load_dotenv()


def get_api_key():
    if "ANTHROPIC_API_KEY" in os.environ:
        return os.environ["ANTHROPIC_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    return None


client = Anthropic(api_key=get_api_key())


def generate_investment_memo(property_data):
    user_message = (
        "Here is the completed underwriting data for this deal. "
        "Write the investment memorandum based only on this information:\n\n"
        + json.dumps(property_data, indent=2, default=str)
    )

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=3000,
        system=MEMO_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ],
    )

    text_blocks = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_blocks)

