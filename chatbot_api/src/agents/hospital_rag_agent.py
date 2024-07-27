import os
from typing import Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from src.chains.hospital_review_chain import reviews_vector_chain
from src.chains.hospital_cypher_chain import hospital_cypher_chain
from src.tools.wait_times import (
    get_current_wait_times,
    get_most_available_hospital,
)


HOSPITAL_AGENT_MODEL = os.getenv("HOSPITAL_AGENT_MODEL")

agent_chat_model = ChatOpenAI(
    model=HOSPITAL_AGENT_MODEL,
    temperature=0,
)


@tool
def explore_patient_experiences(question: str) -> str:
    """
    Useful when you need to answer questions about patient
    experiences, feelings, or any other qualitative question
    that could be answered about a patient using semantic
    search. Not useful for answering objective questions that
    involve counting, percentages, aggregations, or listing facts.
    Use the entire prompt as input to the tool. For instance,
    if the prompt is "Are patients satisfied with their care?",
    the input should be "Are patients satisfied with their care?".
    """

    return reviews_vector_chain.invoke(question)


@tool
def explore_hospital_database(question: str) -> str:
    """
    Useful for answering questions about patients,
    physicians, hospitals, insurance payers, patient review
    statistics, and hospital visit details. Use the entire prompt as
    input to the tool. For instance, if the prompt is "How many visits
    have there been?", the input should be "How many visits have
    there been?".
    """

    return hospital_cypher_chain.invoke(question)


@tool
def get_hospital_wait_time(hospital: str) -> str:
    """
    Use when asked about current wait times
    at a specific hospital. This tool can only get the current
    wait time at a hospital and does not have any information about
    aggregate or historical wait times. Do not pass the word "hospital"
    as input, only the hospital name itself. For example, if the prompt
    is "What is the current wait time at Jordan Inc Hospital?", the
    input should be "Jordan Inc".
    """

    return get_current_wait_times(hospital)


@tool
def find_most_available_hospital(tmp: Any) -> dict[str, float]:
    """
    Use when you need to find out which hospital has the shortest
    wait time. This tool does not have any information about aggregate
    or historical wait times. This tool returns a dictionary with the
    hospital name as the key and the wait time in minutes as the value.
    """

    return get_most_available_hospital(tmp)


agent_tools = [
    explore_patient_experiences,
    explore_hospital_database,
    get_hospital_wait_time,
    find_most_available_hospital,
]

agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful chatbot designed to answer questions
            about patient experiences, patient data, hospitals,
            insurance payers, patient review statistics, hospital
            visit details, wait times, and availability for
            stakeholders in a hospital system.
            """,
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent_llm_with_tools = agent_chat_model.bind_tools(agent_tools)

hospital_rag_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | agent_prompt
    | agent_llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

hospital_rag_agent_executor = AgentExecutor(
    agent=hospital_rag_agent,
    tools=agent_tools,
    verbose=True,
    return_intermediate_steps=True,
)
