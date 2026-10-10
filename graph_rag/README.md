# Simple GraphRAG Example

This project uses LangChain, OpenAI, and Neo4j to build a simple knowledge graph from example text and answer questions based on that graph.

## Prerequisites

1. Install Neo4j Desktop: https://neo4j.com/download/

## Workflow

1. Verify the Neo4j connection.
2. Extract entities and relationships from the example text and save them to the Neo4j graph.
3. Ask natural-language questions against the stored graph.

## File structure

| File | Description |
| --- | --- |
| `1_test_connection.py` | Tests the Neo4j connection using the credentials in `.env`. |
| `2_build_graph.py` | Uses the OpenAI model to extract a knowledge graph from text and stores it in Neo4j. |
| `3_ask_graph.py` | Reads the Neo4j graph schema and answers questions with `GraphCypherQAChain`. |
| `requirements.txt` | Package version list for the current environment. |

## Requirements

- Python 3.10 or newer recommended
- OpenAI API key
- Neo4j database

## Install packages

Create a virtual environment, then install the required packages.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U langchain langchain-openai langchain-neo4j python-dotenv
```

If you want to match the same environment using `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

For macOS:

```bash
pip install -r requirements_macos.txt
```

## Environment variables

Create a `.env` file in the project root and fill in the values below.

```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=neo4j+s://your-neo4j-host
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

You can also add the model name and database name if needed.

```env
OPENAI_MODEL=gpt-5.5
NEO4J_DATABASE=neo4j
```

If `OPENAI_MODEL` is not specified, the code uses `gpt-5.5` by default.

## How to run

### 1. Test the Neo4j connection

```bash
python 1_test_connection.py
```

If the connection is successful, the following message is printed:

```text
Neo4j connection successful!
```

### 2. Create the knowledge graph

```bash
python 2_build_graph.py
```

This script extracts nodes and relationships from the text below.

```text
Kim Min-su was responsible for the payment system refactoring.
The payment system refactoring was a project aimed at reducing system failure rates.
The payment system refactoring was jointly carried out by the security team and the platform team.
```

The extracted graph is saved to Neo4j as `Entity` nodes. Each node receives a type label such as `Person`, `Project`, `Team`, `Metric`, `System`, or `Unknown`.

The relationship types are as follows.

| Relationship | Meaning |
| --- | --- |
| `RESPONSIBLE_FOR` | A person is responsible for a project or task |
| `AIMS_TO_REDUCE` | A project is intended to reduce a metric |
| `COLLABORATED_ON` | Teams jointly work on a project |
| `RELATED_TO` | A general relationship that does not fit the above types |

### 3. Ask questions about the graph

```bash
python 3_ask_graph.py
```

The current example question is:

```text
What is the relationship between Kim Min-su and the security team?
```

`GraphCypherQAChain` uses the Neo4j schema to generate a Cypher query and turns the result into a natural-language answer.

## Check in Neo4j

You can inspect the generated graph in Neo4j Desktop with the following Cypher query:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
```

If you want to see only the nodes, run:

```cypher
MATCH (n)
RETURN n
```
