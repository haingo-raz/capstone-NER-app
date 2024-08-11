from typing import List, Literal
import os
import json
import spacy
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from textblob import TextBlob
import streamlit as st
import uuid
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessageGraph


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


template = """Your job is to get information from a user by asking the following questions one by one.

You should get the following information from them:

- What the name of the user is
- What is their age
- What kind of foods they like
- What kind of foods they dislike
- What is their dietary restrictions or special needs
- What is their eating preferences

If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.

After you are able to discern all the information, call the relevant tool, and return a json."""

# Function to prepare system messages for the LLM
def get_messages_info(messages):
    return [SystemMessage(content=template)] + messages

# Define the data model for the user profile
class PromptInstructions(BaseModel):
    """Instructions on how to prompt the LLM."""
    name: str = ""
    age: int = 0
    liked_foods: List[str] = []
    disliked_foods: List[str] = []
    special_needs: List[str] = []
    eating_preferences: List[str] = []

# Initialize the LLM model
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
llm_with_tool = llm.bind_tools([PromptInstructions])

# Define the chain of operations
chain = get_messages_info | llm_with_tool

# Load and configure spaCy NER model
nlp_ner = spacy.load("./NER/model-best")
nlp_ner.add_pipe('sentencizer')

# Function to extract entities from text
def extract_entities(text):
    doc = nlp_ner(text)
    entities = {
        "liked_foods": [],
        "disliked_foods": [],
        "eating_preferences": [],
        "special_needs": []
    }
    ner_tags = []

    for ent in doc.ents:
        if not any(ent.start_char >= start and ent.end_char <= end for _, start, end, _ in ner_tags):
            if ent.label_ == 'FOOD':
                sentence = next((sent for sent in doc.sents if ent.text in sent.text), None)
                if sentence:
                    blob = TextBlob(sentence.text)
                    sentiment = blob.sentiment.polarity
                    if sentiment < 0:
                        entities["disliked_foods"].append(ent.text)
                    else:
                        entities["liked_foods"].append(ent.text)
                else:
                    entities["liked_foods"].append(ent.text)
            elif ent.label_ == 'PREFERENCE':
                entities["eating_preferences"].append(ent.text)
            elif ent.label_ == 'SPECIALNEED':
                entities["special_needs"].append(ent.text)

    return entities

# Define the prompt for final user profile
prompt_system = """Based on the following requirements, return a json format of the user profile you gathered:

{reqs}"""

# Function to get the prompt messages
def get_prompt_messages(messages: list):
    tool_call = None
    other_msgs = []
    user_message = None
    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls:
            tool_call = m.tool_calls[0]["args"]
        elif isinstance(m, ToolMessage):
            continue
        elif isinstance(m, HumanMessage):
            user_message = m.content
        elif tool_call is not None:
            other_msgs.append(m)
            
    if user_message:
        try:
            ner_entities = extract_entities(user_message)
        except Exception as e:
            st.write(f"Error extracting entities: {e}")
            ner_entities = {"liked_foods": [], "disliked_foods": [], "eating_preferences": [], "special_needs": []}

    if tool_call:
        tool_call["liked_foods"] = tool_call.get("liked_foods", []) + ner_entities["liked_foods"]
        tool_call["disliked_foods"] = tool_call.get("disliked_foods", []) + ner_entities["disliked_foods"]
        tool_call["eating_preferences"] = tool_call.get("eating_preferences", []) + ner_entities["eating_preferences"]
        tool_call["special_needs"] = tool_call.get("special_needs", []) + ner_entities["special_needs"]
    
    return [SystemMessage(content=prompt_system.format(reqs=json.dumps(tool_call, indent=4)))] + other_msgs

# Define the state transition function
def get_state(messages) -> Literal["add_tool_message", "info", "_end_"]:
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_tool_message"
    elif not isinstance(messages[-1], HumanMessage):
        return END
    return "info"

# Create and configure the workflow graph
memory = MemorySaver()
workflow = MessageGraph()
workflow.add_node("info", chain)
workflow.add_node("prompt", get_prompt_messages | llm)

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

# Streamlit interface for interactive chatbot
def run_chatbot():
    st.title("FoodEasy Assistant")
    st.markdown("""
    Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
    Please provide the following details to get started.
    """)
    
    # Initialize session state if not already
    if 'responses' not in st.session_state:
        st.session_state.responses = {
            "name": "",
            "age": "",
            "liked_foods": [],
            "disliked_foods": [],
            "special_needs": [],
            "eating_preferences": []
        }
        st.session_state.step = "start"  # Start the sequence with initial step
    
    user_input = st.text_input("You:", "")
    
    if user_input:
        if st.session_state.step == "start":
            # Immediately ask the first question
            st.session_state.step = "name"
            st.write("What is your name?")
        else:
            # Stream the user input through the graph
            output = None
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            
            for output in graph.stream([HumanMessage(content=user_input)], config=config, stream_mode="updates"):
                last_message = next(iter(output.values()))
                st.write(f"AI: {last_message.content}")

            # Update session state based on current step
            responses = st.session_state.responses
            step = st.session_state.step
            
            if step == "name":
                st.session_state.responses["name"] = user_input
                st.session_state.step = "age"
                st.write("What is your age?")
            elif step == "age":
                try:
                    age = int(user_input)
                    st.session_state.responses["age"] = age
                    st.session_state.step = "liked_foods"
                    st.write("What kind of foods do you like?")
                except ValueError:
                    st.write("Please enter a valid age.")
            elif step == "liked_foods":
                st.session_state.responses["liked_foods"].append(user_input)
                st.session_state.step = "disliked_foods"
                st.write("What kind of foods do you dislike?")
            elif step == "disliked_foods":
                st.session_state.responses["disliked_foods"].append(user_input)
                st.session_state.step = "special_needs"
                st.write("Do you have any dietary restrictions or special needs?")
            elif step == "special_needs":
                st.session_state.responses["special_needs"].append(user_input)
                st.session_state.step = "eating_preferences"
                st.write("What are your eating preferences?")
            elif step == "eating_preferences":
                st.session_state.responses["eating_preferences"].append(user_input)
                st.session_state.step = "done"
                st.write("Thank you! Processing your information.")
                
                # Call the tool with collected responses
                output_json = {
                    "name": st.session_state.responses["name"],
                    "age": st.session_state.responses["age"],
                    "liked_foods": st.session_state.responses["liked_foods"],
                    "disliked_foods": st.session_state.responses["disliked_foods"],
                    "special_needs": st.session_state.responses["special_needs"],
                    "eating_preferences": st.session_state.responses["eating_preferences"]
                }
                st.write(f"Processed Data: {json.dumps(output_json, indent=4)}")
            elif step == "done":
                st.write("Thank you! Your meal plan is being generated.")
                st.stop()
    
    st.button("Submit")

if _name_ == "_main_":
    run_chatbot()