import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.database.neo4j_schema import Neo4jSchemaExplorer, GraphSchema
from src.database.neo4j_connection import Neo4jConnection

@pytest.fixture
def mock_neo4j_connection():
    with patch('src.database.neo4j_schema.Neo4jConnection') as mock_conn:
        # Mock the connection instance
        connection_instance = MagicMock()
        mock_conn.return_value = connection_instance
        
        # Mock verify_connectivity
        connection_instance.verify_connectivity.return_value = True
        
        # Mock session context manager
        session = MagicMock()
        connection_instance.driver.session.return_value.__enter__.return_value = session
        
        # Mock the context manager for the connection itself
        connection_instance.__enter__.return_value = connection_instance
        connection_instance.__exit__.return_value = None
        
        yield {
            'connection': mock_conn,
            'instance': connection_instance,
            'session': session
        }

def test_get_schema_success(mock_neo4j_connection):
    # Configure mock session to return our test data
    mock_session = mock_neo4j_connection['session']
    
    # Create a data object for each call to run().data()
    data_calls = [
        [{'label': 'Patent'}, {'label': 'Inventor'}],  # for db.labels()
        [{'relationshipType': 'CITES'}, {'relationshipType': 'INVENTED_BY'}],  # for db.relationshipTypes()
        [{'propertyKey': 'title'}, {'propertyKey': 'date'}]  # for db.propertyKeys()
    ]
    
    # Set up the mock to return different data for each call
    mock_run = MagicMock()
    mock_run.data.side_effect = data_calls
    mock_session.run.return_value = mock_run
    
    # Create explorer instance and get schema
    explorer = Neo4jSchemaExplorer()
    schema = explorer.get_schema()
    
    # Verify the results
    assert isinstance(schema, GraphSchema)
    assert schema.node_labels == ['Patent', 'Inventor']
    assert schema.relationship_types == ['CITES', 'INVENTED_BY']
    assert schema.property_keys == ['title', 'date']

def test_get_node_properties_success(mock_neo4j_connection):
    # Prepare mock data
    mock_properties = [{'key': 'title'}, {'key': 'abstract'}, {'key': 'filing_date'}]
    
    # Configure mock session
    mock_session = mock_neo4j_connection['session']
    mock_run = MagicMock()
    mock_run.data.return_value = mock_properties
    mock_session.run.return_value = mock_run
    
    # Create explorer instance and get node properties
    explorer = Neo4jSchemaExplorer()
    result = explorer.get_node_properties('Patent')
    
    # Verify the results
    assert result == {'Patent': ['title', 'abstract', 'filing_date']}
    mock_session.run.assert_called_once()

def test_get_relationship_properties_success(mock_neo4j_connection):
    # Prepare mock data
    mock_properties = [{'key': 'date'}, {'key': 'type'}]
    
    # Configure mock session
    mock_session = mock_neo4j_connection['session']
    mock_run = MagicMock()
    mock_run.data.return_value = mock_properties
    mock_session.run.return_value = mock_run
    
    # Create explorer instance and get relationship properties
    explorer = Neo4jSchemaExplorer()
    result = explorer.get_relationship_properties('CITES')
    
    # Verify the results
    assert result == {'CITES': ['date', 'type']}
    mock_session.run.assert_called_once()

def test_connection_failure(mock_neo4j_connection):
    # Mock connection failure
    mock_neo4j_connection['instance'].verify_connectivity.return_value = False
    
    # Create explorer instance
    explorer = Neo4jSchemaExplorer()
    
    # Test that ConnectionError is raised
    with pytest.raises(ConnectionError):
        explorer.get_schema()

def test_graph_schema_display(capsys):
    # Create a test schema
    schema = GraphSchema(
        node_labels=['Patent', 'Inventor'],
        relationship_types=['CITES', 'INVENTED_BY'],
        property_keys=['title', 'date']
    )
    
    # Call display method
    schema.display()
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Verify the output format
    expected_output = """Node Labels:
- Patent
- Inventor

Relationship Types:
- CITES
- INVENTED_BY

Property Keys (across all nodes and relationships):
- title
- date
"""
    assert captured.out == expected_output
