import os
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from src.utils.docx_ingest import simple_search
from langchain.chains import LLMChain
from langchain.schema import Document
from src.utils.ollama_llm import generate_with_ollama

USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() in ("1", "true", "yes")

HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="reviews",
    node_label="Review",
    text_node_properties=[
        "physician_name",
        "patient_name",
        "text",
        "hospital_name",
    ],
    embedding_node_property="embedding",
)

review_template = """Your job is to use patient
reviews to answer questions about their experience at a hospital. Use
the following context to answer questions. Be as detailed as possible, but
don't make up any information that's not from the context. If you don't know
an answer, say you don't know.
{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=review_template)
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [review_system_prompt, review_human_prompt]

review_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

if USE_OLLAMA:
    # Simple wrapper LLMChain for Ollama: use LLMChain with a callable that calls generate_with_ollama
    def _ollama_run(inputs: dict) -> str:
        prompt_text = review_prompt.format(context=inputs.get("context", ""), question=inputs.get("question", ""))
        return generate_with_ollama(prompt_text, model=os.getenv("HOSPITAL_QA_MODEL"))

    reviews_vector_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model=HOSPITAL_QA_MODEL, temperature=0),
        chain_type="stuff",
        retriever=neo4j_vector_index.as_retriever(k=12),
    )
    # Keep prompt on the combine chain but the actual generation will be routed via generate_with_ollama in uploaded_reviews_chain
    reviews_vector_chain.combine_documents_chain.llm_chain.prompt = review_prompt
else:
    reviews_vector_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model=HOSPITAL_QA_MODEL, temperature=0),
        chain_type="stuff",
        retriever=neo4j_vector_index.as_retriever(k=12),
    )
    reviews_vector_chain.combine_documents_chain.llm_chain.prompt = review_prompt


def uploaded_docs_retriever(question: str) -> str:
    """Search uploaded docs (DOCX) stored locally and return a context string."""
    results = simple_search(question, k=6)
    if not results:
        return ""

    # Combine top results into one context
    docs = [Document(page_content=r["text"]) for r in results]
    combined = "\n\n---\n\n".join([d.page_content for d in docs])
    return combined


def uploaded_reviews_chain(question: str) -> str:
    """LLM answer over uploaded docs only."""
    context = uploaded_docs_retriever(question)
    if not context:
        return "No uploaded documents found matching the query."

    llm = ChatOpenAI(model=HOSPITAL_QA_MODEL, temperature=0)
    chain = LLMChain(llm=llm, prompt=review_prompt)
    return chain.run({"context": context, "question": question})
