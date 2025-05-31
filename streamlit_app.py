import streamlit as st
import random
import time
import os
import logging
import vertexai
from vertexai import agent_engines
# from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv()
# log = logging.getLogger(__name__)

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket="gs://" + os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET'),
)

st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def parse_event_content(event: dict) -> list:
    """
    Parses the 'content' section of an event dictionary to extract text,
    function calls, or function responses from the 'parts' list.
    
    Args:
        event: The event dictionary to parse.
    
    Returns:
        A list of tuples. Each tuple contains (events type, content)
        Returns an empty list if the structure is invalid or no
        relevant parts are found.
    """
    results = []

    content = event.get('content')
    if not isinstance(content, dict):
        return results # Return empty list if content is missing/wrong type

    parts = content.get('parts')
    if not isinstance(parts, list):
        return results # Return empty list if parts is missing/wrong type

    # Iterate through each dictionary in the 'parts' list
    for part in parts:
        if not isinstance(part, dict):
            results.append(('unknown', part)) # Handle non-dict items
            continue # Skip to the next item
        
        if 'text' in part:
            print(" - - - - - - - - - - - - - - -")
            print('>>> Inside final response <<<')
            print(" - - - - - - - - - - - - - - -")
            print(part['text'])
            results.append(('text', part['text']))
        elif 'function_call' in part:
            print(" - - - - - - - - - - - - - - -")
            print('+++ Inside function call +++')
            print(" - - - - - - - - - - - - - - -")
            print(f"Call Function: {part['function_call']['name']}")
            print(f"Argument: {part['function_call']['args']}")
            # Found a function call part
            results.append(('function_call', part['function_call']))
        elif 'function_response' in part:
            print(" - - - - - - - - - - - - - - - ")
            print(' - Inside function response - ')
            print(" - - - - - - - - - - - - - - - ")
            print(f"Function Response: {part['function_response']['name']}")
            print(f"Response: {part['function_response']['response']}")
            results.append(('function_response', part['function_response']))
        else:
            # The part dictionary doesn't contain any of the expected keys
            print(f'Unknown part: {part}')
            results.append(('unknown', part))
    return results

# Accept user input
if prompt := st.chat_input("What is up?"): # Walrus Operator
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # msg = "hello, I am your assistant."
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)

    # RESOURCE_ID = "projects/662223484770/locations/us-central1/reasoningEngines/710310899822362624"
    RESOURCE_ID = "710310899822362624"
    remote_agent = agent_engines.get(RESOURCE_ID)
    remote_session = remote_agent.create_session(user_id="u_456")
    print(remote_session)
    # remote_agent = reasoning_engines.ReasoningEngine(RESOURCE_ID)
    # print(remote_agent)
    # log.debug(remote_agent.operation_schemas())
    # chatbot_msg = remote_agent.query(input={"messages": [
    #     ("user", prompt)
    # ]})

    chatbot_msg = ""
    for event in remote_agent.stream_query(
        user_id="u_456",
        session_id=remote_session["id"],
        message=prompt,
    ):
        # use parse_event_content to generate all text message
        event_content = parse_event_content(event)
        for event_type, content in event_content:
            if event_type == 'text':
                chatbot_msg = chatbot_msg + content
        

    st.session_state.messages.append({"role": "assistant", "content": chatbot_msg})
    st.chat_message("assistant").write(chatbot_msg)

    