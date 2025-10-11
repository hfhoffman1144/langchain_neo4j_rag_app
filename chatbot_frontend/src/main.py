import os
import requests
import streamlit as st

CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000/hospital-rag-agent")

with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This chatbot interfaces with a
        [LangChain](https://python.langchain.com/docs/get_started/introduction)
        agent designed to answer questions about attorneys, clients,
        cases, legal documents, firm billing, and practice-area knowledge
        for a simulated law firm. The agent uses retrieval-augmented
        generation (RAG) over both structured and unstructured firm data.
        """
    )

    st.header("Example Questions")
    st.markdown("- Which attorneys are in the firm?")
    st.markdown("- Show open cases for client 'Acme Corp' and assigned attorney")
    st.markdown("- Which cases have billing disputes in the last quarter?")
    st.markdown("- What does the case note for case #1234 say about the discovery timeline?")
    st.markdown("- Summarize recent legal memos about employment law in our library")
    st.markdown("- What is the total billed amount by attorney for 2024?")
    st.markdown("- Which attorney has the most cases in the corporate practice area?")
    st.markdown("- Find client contact info for 'Jane Doe'")
    st.markdown("- List all documents mentioning 'non-compete' for client X")


st.title("Hospital System Chatbot")
st.info(
    """Ask me questions about patients, visits, insurance payers, hospitals,
    physicians, reviews, and wait times!"""
)


st.header("Upload DOCX (for RAG over custom documents)")
uploaded_file = st.file_uploader("Upload a .docx file to add to the agent's document store", type=["docx"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        resp = requests.post("http://localhost:8000/upload-docx", files=files)
        if resp.status_code == 200:
            st.success(f"Uploaded: {resp.json().get('id')}")
            st.text(resp.json().get("text_snippet"))
        else:
            st.error(f"Upload failed: {resp.status_code} {resp.text}")
    except Exception as e:
        st.error(f"Error contacting the API: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])

        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])

if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "output": prompt})

    data = {"text": prompt}

    with st.spinner("Searching for an answer..."):
        response = requests.post(CHATBOT_URL, json=data)

        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]

        else:
            output_text = """An error occurred while processing your message.
            This usually means the chatbot failed at generating a query to
            answer your question. Please try again or rephrase your message."""
            explanation = output_text

    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated?", state="complete").info(explanation)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "output": output_text,
            "explanation": explanation,
        }
    )
