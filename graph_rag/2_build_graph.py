import os
import json
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph


load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


class KGNode(BaseModel):
    id: str = Field(description="Node name. Example: Kim Min-su, Payment System Refactoring")
    type: Literal["Person", "Project", "Team", "Metric", "System", "Unknown"]


class KGRelationship(BaseModel):
    source: str = Field(description="Source node id")
    target: str = Field(description="Target node id")
    kind: Literal[
        "RESPONSIBLE_FOR",
        "AIMS_TO_REDUCE",
        "COLLABORATED_ON",
        "RELATED_TO",
    ]


class KGGraph(BaseModel):
    nodes: list[KGNode]
    relationships: list[KGRelationship]


graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=os.getenv("NEO4J_DATABASE"),
)

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
)

structured_llm = llm.with_structured_output(
    KGGraph,
    method="json_schema",
)

text = """
Kim Min-su was responsible for the payment system refactoring.
The payment system refactoring was a project aimed at reducing system failure rates.
The payment system refactoring was jointly carried out by the security team and the platform team.
"""

prompt = f"""
Extract a knowledge graph from the following English text.

Rules:
- Use only information explicitly stated in the text.
- Extract important people, projects, teams, metrics, and systems as nodes.
- Use the following relationship types whenever possible:
  - RESPONSIBLE_FOR: a person is responsible for a project or task
  - AIMS_TO_REDUCE: a project is intended to reduce a certain metric
  - COLLABORATED_ON: teams jointly work on a project
  - RELATED_TO: a general relationship that is difficult to express with the above types
- The source and target of each relationship must be one of the IDs in `nodes`.

Text:
{text}
"""

kg = structured_llm.invoke(prompt)

print("LLM extraction result:")
print(json.dumps(kg.model_dump(), ensure_ascii=False, indent=2))

# Prevent duplicate node creation.
graph.query("""
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.id IS UNIQUE
""")

nodes = [node.model_dump() for node in kg.nodes]
relationships = [rel.model_dump() for rel in kg.relationships]

# Save nodes
graph.query(
    """
    UNWIND $nodes AS node
    MERGE (e:Entity {id: node.id})
    SET e.type = node.type
    """,
    params={"nodes": nodes},
)

# Add type-specific labels so GraphCypherQAChain can better understand the schema.
for node_type in ["Person", "Project", "Team", "Metric", "System", "Unknown"]:
    graph.query(
        f"""
        MATCH (e:Entity {{type: $node_type}})
        SET e:{node_type}
        """,
        params={"node_type": node_type},
    )

# Save relationships
for kind in [
    "RESPONSIBLE_FOR",
    "AIMS_TO_REDUCE",
    "COLLABORATED_ON",
    "RELATED_TO",
]:
    graph.query(
        f"""
        UNWIND $relationships AS rel
        WITH rel
        WHERE rel.kind = $kind
        MATCH (source:Entity {{id: rel.source}})
        MATCH (target:Entity {{id: rel.target}})
        MERGE (source)-[r:{kind}]->(target)
        """,
        params={"relationships": relationships, "kind": kind},
    )

print("Graph created successfully!")
