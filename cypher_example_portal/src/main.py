import streamlit as st
from graph_utils import (
    add_example_cypher_query,
    does_question_exist,
    is_valid_cypher_query,
    fetch_most_similar_question,
)

st.title("Cypher Example Self-Service Portal")

with st.sidebar:
    st.header("About")
    st.markdown(
        """
    This app allows you to add example questions and their corresponding
    Cypher queries to a vector index used by the
    [Hospital System Chatbot](https://github.com/hfhoffman1144/langchain_neo4j_rag_app).

    When you ask the chatbot to generate Cypher queries, it dynamically retrieves
    semantically similar questions and their corresponding Cypher queries from the
    vector index. This context helps the chatbot generate more accurate queries.

    If the chatbot generates an incorrect query for a question, and
    you know the correct query, add it here!
    """
    )

question = st.text_area("Enter an example question:")
cypher = st.text_area("Enter the corresponding Cypher query that answers the question:")

if "validated" not in st.session_state:
    st.session_state.validated = False

if question and cypher:
    if st.button("Validate"):
        if does_question_exist(question):
            st.warning(
                "This question already exists in the example index. Please enter a new question."
            )
        elif not is_valid_cypher_query(cypher):
            st.warning(
                "The Cypher query did not execute successfully. Please enter a valid query."
            )
        else:
            st.session_state.validated = True

if st.session_state.validated:
    st.success("This question does not currently exist in the example index.")
    st.success("The Cypher query executed successfully.")

    similar_question = fetch_most_similar_question(question)

    if similar_question is None:
        st.success("There are currently no example questions in the example index.")

    else:
        st.warning(
            f"""
            The most similar question to this one currently in the
            example index is "{similar_question}" Are you sure you
            want to proceed?
            """
        )

    if st.button("Upload"):
        results = add_example_cypher_query(question, cypher)

        if len(results) == 1:
            st.success(
                f"""
                The question and corresponding Cypher query was added
                to the index with an ID of {results[0]}
                """
            )

            st.session_state.validated = False
