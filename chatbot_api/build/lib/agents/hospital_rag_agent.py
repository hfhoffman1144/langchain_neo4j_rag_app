from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from chains.hospital_review_rag_chain import reviews_vector_qa
from chains.hospital_cypher_chain import hospital_cypher_chain
from tools.wait_times import get_current_wait_times, find_most_available_hospital


tools = [
    Tool(
        name="Reviews",
        func=reviews_vector_qa.run,
        description="""
        Useful when you need to answer questions about patient reviews or experiences. 
        Not useful for answering objective questions that involve counting or aggregation.
        Use the entire prompt as input to the tool. For instance, if the prompt is
        "Are patients satisfied with their care?", the input should be "Are patients
        satisfied with their care?".
        """,
    ),
    Tool(
        name="Graph",
        func=hospital_cypher_chain.run,
        description="""
        Useful for answering questions about patients, physiscians, hospitals, insurance 
        payers, and hospital visit details. Use the entire prompt as input to the tool. 
        For instance, if the prompt is "How many visits have there been?", the input
        should be "How many visits have there been?".
        """,
    ),
    Tool(
        name="Waits",
        func=get_current_wait_times,
        description="""
        Use when asked about current wait times at a specific hospital. This tool can only get
        the current wait time at a hospital and does not have any information about
        aggregate or historical wait times. This tool returns wait times in minutes.
        Do not pass the word "hospital" as input, only the hospital name itself.
        """,
    ),
    Tool(
        name="Availability",
        func=find_most_available_hospital,
        description="""
        Use when you need to find out which hospital has the shortest weight time. This tool 
        does not have any information about aggregate or historical wait times. This tool returns a
        dictionary with the hospital name as the key and the wait time in minutes as the value.
        """,
    ),
]

chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    streaming=True,
    temperature=0,
)

hospital_rag_agent = initialize_agent(
    tools,
    chat_model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    return_intermediate_steps=True,
)
