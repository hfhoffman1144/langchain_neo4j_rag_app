import streamlit as st
import requests


# Define the URL to which you want to send the POST request
url = "http://localhost:8000/hospital-rag-agent"

st.title("Hospital RAG Chat Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Define the data you want to include in the POST request (if any)
    data = {
        'text': prompt
    }

    # Make the POST request
    response = requests.post(url, json=data).text

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})