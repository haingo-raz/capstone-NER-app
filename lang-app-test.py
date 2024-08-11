import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph import END, START, MessageGraph
from langgraph.checkpoint.memory import MemorySaver
import json
import uuid
from typing import List, Literal

# Define your template
template = """Your job is to get information from a user by asking them these questions one by one.
You should get the following information from them:
- What the name of the user is
- What is their age
- What kind of foods they like
- What kind of foods they dislike
- What is their dietary restrictions or special needs
- What is their eating preferences
If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.
After you are able to discern all the information, return a JSON object with the gathered information."""

def get_messages_info(messages):
    return [SystemMessage(content=template)] + messages

class PromptInstructions(BaseModel):
    name: str
    age: int
    liked_foods: List[str]
    disliked_foods: List[str]
    special_needs: List[str]
    eating_preferences: List[str]

# Initialize LLM and chain
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
llm_with_tool = llm.bind_tools([PromptInstructions])
chain = get_messages_info | llm_with_tool

# Define prompt system
prompt_system = """Based on the following requirements, return a JSON format of the user profile you gathered:
{reqs}"""

def get_prompt_messages(messages: list):
    tool_call = None
    other_msgs = []
    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls:
            tool_call = m.tool_calls[0]["args"]
        elif isinstance(m, ToolMessage):
            continue
        elif isinstance(m, HumanMessage):
            other_msgs.append(m)
    return [SystemMessage(content=prompt_system.format(reqs=json.dumps(tool_call, indent=4)))] + other_msgs

prompt_gen_chain = get_prompt_messages | llm

def get_state(messages) -> Literal["add_tool_message", "info", "__end__"]:
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_tool_message"
    elif not isinstance(messages[-1], HumanMessage):
        return END
    return "info"

memory = MemorySaver()
workflow = MessageGraph()
workflow.add_node("info", chain)
workflow.add_node("prompt", prompt_gen_chain)

@workflow.add_node
def add_tool_message(state: list):
    return ToolMessage(
        content="Prompt generated!", tool_call_id=state[-1].tool_calls[0]["id"]
    )

workflow.add_conditional_edges("info", get_state)
workflow.add_edge("add_tool_message", "prompt")
workflow.add_edge("prompt", END)
workflow.add_edge(START, "info")
graph = workflow.compile(checkpointer=memory)

import spacy
from textblob import TextBlob

# Load spaCy model
nlp_ner = spacy.load("./NER/model-best")
nlp_ner.add_pipe('sentencizer')

# Initialize the session state variables
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "age": None,
        "liked_foods": [],
        "disliked_foods": [],
        "eating_preferences": [],
        "special_needs": [],
    }
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start! Type anything in the chatbox to begin."}]

# Function to extract entities
def extract_entities(text):
    doc = nlp_ner(text)
    entities = {
        "liked_foods": [],
        "disliked_foods": [],
        "eating_preferences": [],
        "special_needs": []
    }
    for ent in doc.ents:
        if ent.label_ == 'FOOD':
            blob = TextBlob(ent.text)
            sentiment = blob.sentiment.polarity
            if sentiment < 0:
                entities["disliked_foods"].append(ent.text)
            else:
                entities["liked_foods"].append(ent.text)
        elif ent.label_ == 'PREFERENCE':
            entities["eating_preferences"].append(ent.text)
        elif ent.label_ == 'SPECIALNEED':
            entities["special_needs"].append(ent.text)
    return entities

# Streamlit UI
st.title("FoodEasy Assistant")
st.markdown("Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile. Please provide the following details to get started.")

with st.container(height=410):
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input
prompt = st.chat_input("Type your response here...", key='user_input')

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
if prompt:    
    # Process user input
    output = None
    for output in graph.stream([HumanMessage(content=prompt)], config=config, stream_mode="updates"):
        last_message = next(iter(output.values()))

    st.session_state['messages'].append({"role": "user", "content": prompt})
    st.session_state['messages'].append({"role": "assistant", "content": last_message.content})
    
    if output and "prompt" in output:
        st.session_state['messages'].append({"role": "assistant", "content": "Done"})


# Display user profile
sidebar = st.sidebar
sidebar.markdown("Gathered user information:")
sidebar.write(st.session_state.user_profile)