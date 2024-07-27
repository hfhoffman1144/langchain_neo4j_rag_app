import os
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_Password")
NEO4J_CYPHER_EXAMPLES_INDEX_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_INDEX_NAME")
NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY = os.getenv(
    "NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY"
)
NEO4J_CYPHER_EXAMPLES_NODE_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_NODE_NAME")
NEO4J_CYPHER_EXAMPLES_METADATA_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_METADATA_NAME")


NEO4J_GRAPH = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

NEO4J_GRAPH.refresh_schema()

NEO4J_VECTOR_INDEX = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=NEO4J_CYPHER_EXAMPLES_INDEX_NAME,
    node_label=NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY.capitalize(),
    text_node_properties=[
        NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY,
    ],
    text_node_property=NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY,
    embedding_node_property="embedding",
)


def search_node_by_str_property(
    graph: Neo4jGraph, node_name: str, property_name: str, value: str
) -> list[dict]:
    """
    Search a Neo4j graph for nodes that match a given string property value.
    """

    cypher_query = (
        f'MATCH (p:{node_name}) WHERE p.{property_name} = "{value}" RETURN p;'
    )

    return graph.query(cypher_query)


def does_question_exist(question: str) -> bool:
    """
    Determine whether a Cypher example question exists.
    """

    results = search_node_by_str_property(
        graph=NEO4J_GRAPH,
        node_name=NEO4J_CYPHER_EXAMPLES_NODE_NAME,
        property_name=NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY,
        value=question.lower().strip(),
    )

    return len(results) > 0


def is_valid_cypher_query(query: str) -> bool:
    """
    Determine whether a Cypher query successfully runs
    """

    try:
        NEO4J_GRAPH.query(query)
        return True

    except Exception:
        return False


def fetch_most_similar_question(question: str) -> str | None:
    """
    Perform semantic search to find the most similar question to
    the input.
    """

    documents = NEO4J_VECTOR_INDEX.similarity_search(question)

    if len(documents) == 0:
        return None

    return documents[0].page_content


def add_example_cypher_query(question: str, cypher: str) -> str:
    """
    Add a question and corresponding Cypher query to a Neo4j
    vector index. This can be used to dynamically augment prompts
    used for Text-To-Cypher problems.
    """

    cypher_metadata_key = NEO4J_CYPHER_EXAMPLES_METADATA_NAME

    node_id = NEO4J_VECTOR_INDEX.add_texts(
        texts=[question.lower().strip()],
        metadatas=[{cypher_metadata_key: cypher}],
    )

    return node_id
