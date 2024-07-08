import os
import json
from typing_extensions import override
from PIL import ImageFile

import streamlit as st
from openai import OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
from openai.assistant import AssistantEventHandler

# Get secrets
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", st.secrets["OPENAI_API_KEY"])

# Initialise the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def save_profile_to_json(profile, filename="user_profile.json"):
    with open(filename, "w") as f:
        json.dump(profile, f)

def render_custom_css() -> None:
    """
    Applies custom CSS
    """
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden}
        footer {visibility: hidden}
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

def initialise_session_state():
    """
    Initialise session state variables
    """
    if "file" not in st.session_state:
        st.session_state.file = None

    if "assistant_text" not in st.session_state:
        st.session_state.assistant_text = [""]

    for session_state_var in ["file_uploaded", "read_terms"]:
        if session_state_var not in st.session_state:
            st.session_state[session_state_var] = False

    for session_state_var in ["code_input", "code_output"]:
        if session_state_var not in st.session_state:
            st.session_state[session_state_var] = []

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text: Text) -> None:
        st.session_state.assistant_text[-1] += text.value

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        st.session_state.assistant_text[-1] += delta.value

    @override
    def on_text_done(self, text: Text):
        st.session_state.assistant_text.append("")
        st.write(st.session_state.assistant_text[-2])

    @override
    def on_tool_call_created(self, tool_call: ToolCall):
        pass

    @override
    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCallDelta):
        pass

    @override
    def on_tool_call_done(self, tool_call: ToolCall):
        pass

    @override
    def on_image_file_done(self, image_file: ImageFile):
        pass

    def on_timeout(self):
        st.error("The API call timed out.")
        st.stop()
