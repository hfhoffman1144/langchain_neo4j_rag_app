import streamlit as st
from graph_utils import (
    add_example_cypher_query,
    does_question_exist,
    is_valid_cypher_query,
    fetch_most_similar_question,
)

st.title("Cypher Example Self-Service Portal")

with st.sidebar:
    st.title("About")
    st.info(
        """
    Add example questions and corresponding Cypher queries to be used
    as context for the Hospital System Chatbot. Your query must execute
    successfully in the existing database, and ideally be reviewed by
    others, to make it into the database.
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
