import os
import requests
import streamlit as st




# Define the URL to which you want to send the POST request
CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000/hospital-rag-agent")


with st.sidebar:
  
   st.header("About")
   st.markdown("""
       This chatbot interfaces with a [LangChain](https://python.langchain.com/docs/get_started/introduction) agent
       designed to answer questions about the hospitals, patients, visits, physicians, and insurance payers in
       a fake hospital system. The agent uses retrieval-augment generation (RAG)
       over both structured and unstructured data that has been synthetically generated. All data, code, and documentation are available on
       [GitHub](https://github.com/hfhoffman1144/langchain_neo4j_rag_app).
   """)
  
   st.header("Example Questions")
   st.markdown("- Which hospitals are in the hospital system?")
   st.markdown("- What is the current wait time at wallace-hamilton hospital?")
   st.markdown("- At which hospitals are patients complaining about billing and insurance issues?")
   st.markdown("- What is the average duration in days for emergency visits?")
   st.markdown("- What are patients saying about the nursing staff at Castaneda-Hardy?")
   st.markdown("- What was the total billing amount charged to each payer for 2023?")
   st.markdown("- What is the average billing amount for medicaid visits?")
   st.markdown("- Which physician has the lowest average visit duration in days?")
   st.markdown("- How much was billed for patient 789's stay?")
   st.markdown("- How much was billed for patient 789's stay?")
   st.markdown("- Which state had the largest percent increase in medicaid visits from 2022 to 2023?")


st.title("Hospital System Chatbot")
st.info(
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
               "An error occurred while processing your query. Please try again."
           )
           explanation = output_text


   # Display assistant response in chat message container
   st.chat_message("assistant").markdown(output_text)
   st.status("How was this generated", state="complete").info(explanation)
          
   # Add assistant response to chat history
   st.session_state.messages.append({"role": "assistant", "output": output_text, "explanation": explanation})
