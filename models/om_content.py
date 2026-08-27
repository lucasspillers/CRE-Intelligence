import os
import re
import json
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from prompts.om_prompt import OM_SYSTEM_PROMPT


def get_api_key():
    if "ANTHROPIC_API_KEY" in os.environ:
        return os.environ["ANTHROPIC_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    return None


client = Anthropic(api_key=get_api_key())

FALLBACK_NARRATIVE = {
    "executive_summary": "An executive summary could not be generated for this property. Please review the underwriting data manually.",
    "property_overview": "A property overview could not be generated for this property. Please review the underwriting data manually.",
    "market_overview": "Market information has not yet been provided. Once market data or a market study is uploaded, this section will summarize submarket fundamentals, demand drivers, and comparable transactions.",
    "tenant_overview": "Tenant information has not yet been provided. Once lease documents or a rent roll are uploaded, this section will automatically summarize tenant composition, lease rollover, and occupancy.",
    "investment_highlights": ["Investment highlights have not yet been generated. Please review the underwriting data manually."],
    "cash_flow_commentary": "Cash flow commentary could not be generated for this property. Please review the cash flow schedule manually.",
}


def strip_code_fence(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json_object(text):
    text = strip_code_fence(text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def generate_om_narrative(property_data):
    user_message = (
        "Here is the completed underwriting data for this deal. "
        "Write the six OM sections based only on this information:\n\n"
        + json.dumps(property_data, indent=2, default=str)
    )

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2500,
        system=OM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text_blocks = [block.text for block in message.content if block.type == "text"]
    raw_response = extract_json_object("\n".join(text_blocks))

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(raw_response.replace("\n", "\\n"))
        except json.JSONDecodeError:
            return dict(FALLBACK_NARRATIVE)

    for key in FALLBACK_NARRATIVE:
        if key not in parsed or not parsed[key]:
            parsed[key] = FALLBACK_NARRATIVE[key]
    return parsed
