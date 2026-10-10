import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE"),
)
graph.refresh_schema()

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
)

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    validate_cypher=True,
    allow_dangerous_requests=True,
)

print("Graph schema:")
print(graph.schema)

questions = [
    "What is the relationship between Kim Min-su and the security team?",
]

for question in questions:
    print("\nQuestion:", question)
    result = chain.invoke({"query": question})
    print("Answer:", result["result"])
