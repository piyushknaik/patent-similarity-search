# Patent Similarity Search

A Python application for exploring and analyzing patent data using Neo4j graph database and similarity search techniques.

## Prerequisites

- Python 3.12 or higher
- Neo4j Database
- Virtual Environment (recommended)

## Quick Start

```bash
# Clone and enter the repository
git clone https://github.com/piyushknaik/patent-similarity-search.git
cd patent-similarity-search

# Set up Python environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure Neo4j connection
cp .env.example .env
# Edit .env with your Neo4j credentials:
# NEO4J_URI=neo4j+s://<your-instance-id>.databases.neo4j.io
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=your-password
# NEO4J_DATABASE=neo4j
```

## Running the Application

The application provides several utilities for exploring Neo4j database schema:

1. View complete database schema:
```python
from src.database.neo4j_schema import Neo4jSchemaExplorer

# Create schema explorer instance
explorer = Neo4jSchemaExplorer()

# Get and display complete schema
schema = explorer.get_schema()
schema.display()
```

2. Get properties for a specific node label:
```python
# Get properties for Patent nodes
node_props = explorer.get_node_properties("Patent")
print(f"Patent node properties: {node_props}")
```

3. Get properties for a specific relationship type:
```python
# Get properties for CITES relationships
rel_props = explorer.get_relationship_properties("CITES")
print(f"CITES relationship properties: {rel_props}")
```

## Running Tests

The project uses pytest for testing. To run the tests:

1. Install development dependencies:
```bash
pip install pytest pytest-mock
```

2. Run all tests:
```bash
pytest tests/ -v
```

3. Run specific test file:
```bash
pytest tests/test_neo4j_schema.py -v
```

4. Run tests with coverage:
```bash
pip install pytest-cov
pytest tests/ --cov=src/
```

## Project Structure

```
patent-similarity-search/
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── neo4j_connection.py
│   │   └── neo4j_schema.py
│   ├── data/
│   ├── embeddings/
│   └── utils/
├── tests/
│   ├── __init__.py
│   └── test_neo4j_schema.py
├── config/
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Error Handling

The application includes proper error handling for:
- Database connection issues
- Invalid node labels or relationship types
- Missing environment variables

Example error handling:
```python
try:
    explorer = Neo4jSchemaExplorer()
    schema = explorer.get_schema()
except ConnectionError as e:
    print(f"Failed to connect to Neo4j database: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
```
