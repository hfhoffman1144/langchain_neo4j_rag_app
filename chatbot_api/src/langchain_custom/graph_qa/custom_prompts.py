# flake8: noqa
from langchain_core.prompts.prompt import PromptTemplate

CYPHER_GENERATION_WITH_EXAMPLES_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}

Example Cypher queries for this schema:
{example_queries}

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

The question is:
{question}"""

CYPHER_GENERATION_WITH_EXAMPLES_PROMPT = PromptTemplate(
    input_variables=["schema", "example_queries", "question"],
    template=CYPHER_GENERATION_WITH_EXAMPLES_TEMPLATE,
)
