from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from chains.hospital_review_rag_chain import reviews_vector_qa
from chains.hospital_cypher_chain import hospital_cypher_chain
from tools.wait_times import get_current_wait_times


tools = [
    Tool(
        name="Reviews",
        func=reviews_vector_qa.run,
        description="""
        Useful when you need to answer questions about patient reviews or experiences. 
        Not useful for answering objective questions that involve counting or aggregation.
        Use full question as input.
        """,
    ),
    Tool(
        name="Graph",
        func=hospital_cypher_chain.run,
        description="""
        Useful for answering questions about patients, physiscians, hospitals, insurance 
        payers, and hospital visit details. Use full question as input.
        """,
    ),
    Tool(
        name="Waits",
        func=get_current_wait_times,
        description="""
        Use when asked about current wait times at a hospital. This tool can only get
        the current wait time at a hospital and does not have any information about
        aggregate or historical wait times. This tool returns wait times in minutes.
        Only pass the hospital name as input and don't include the word "hospital".
        """,
    ),
]

chat_model = (
    ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        streaming=True,
        temperature=0,
    )
)

hospital_rag_agent = initialize_agent(
    tools,
    chat_model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)
