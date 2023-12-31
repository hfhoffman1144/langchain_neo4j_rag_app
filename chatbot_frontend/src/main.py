import os
import requests
import streamlit as st


# Define the URL to which you want to send the POST request
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000/hospital-rag-agent")

st.title("Hospital System RAG Chatbot")
st.subheader(
    "Ask me questions about patients, visits, insurance payers, hospitals, physicians, reviews, and wait times!"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
        
    with st.chat_message(message["role"]):
        
        if "output" in message.keys():
            
            st.markdown(message["output"])
        
        if "explanation" in message.keys():
            
            with st.status("How was this generated", state="complete"):
                
                st.info(message["explanation"])
                            
# React to user input
if prompt := st.chat_input("What do you want to know?"):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "output": prompt})

    # Define the data you want to include in the POST request
    data = {"text": prompt}

    with st.spinner("Searching for an answer..."):
        response = requests.post(CHATBOT_URL, json=data)

        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]

        else:
            output_text = (
                "An error occured while processing your query. Please try again."
            )
            explanation = output_text

    # Display assistant response in chat message container
    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated", state="complete").info(explanation)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "output": output_text, "explanation": explanation})
