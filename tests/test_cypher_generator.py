import pytest
from unittest.mock import MagicMock, patch
from src.database.cypher_generator import CypherQueryGenerator, QueryGeneratorConfig, CypherQuery
from src.database.neo4j_schema import GraphSchema

@pytest.fixture
def mock_schema():
    return GraphSchema(
        node_labels=["Patent", "Inventor"],
        relationship_types=["INVENTED_BY", "CITES"],
        property_keys=["patent_number", "title", "first_name", "last_name"]
    )

@pytest.fixture
def mock_llm_response():
    return CypherQuery(query="""
        MATCH (p:Patent)-[:INVENTED_BY]->(i:Inventor)
        RETURN p.patent_number as related_patent_number,
               p.title as patent_title,
               i.first_name as inventor_first_name,
               i.last_name as inventor_last_name
    """)

@pytest.fixture
def config():
    return QueryGeneratorConfig(
        model_name="test-model",
        temperature=0,
        api_key="test-key",
        api_base="test-base"
    )

@pytest.fixture
def mock_schema_explorer(mock_schema):
    with patch('src.database.cypher_generator.Neo4jSchemaExplorer') as mock:
        instance = mock.return_value
        instance.get_schema.return_value = mock_schema
        yield instance

def test_cypher_query_generator_initialization(config):
    generator = CypherQueryGenerator(config)
    assert generator.config == config
    assert generator.llm is not None
    assert generator.schema_explorer is not None
    assert generator.parser is not None
    assert generator.prompt is not None
    assert generator.query_chain is not None

def test_format_schema(config, mock_schema):
    generator = CypherQueryGenerator(config)
    formatted_schema = generator._format_schema(mock_schema)
    
    assert "Node Labels:" in formatted_schema
    assert "Patent" in formatted_schema
    assert "Inventor" in formatted_schema
    assert "Relationship Types:" in formatted_schema
    assert "INVENTED_BY" in formatted_schema
    assert "CITES" in formatted_schema
    assert "Property Keys:" in formatted_schema
    assert "patent_number" in formatted_schema
    assert "title" in formatted_schema

@patch('langchain_community.chat_models.ChatOpenAI')
def test_generate_query_success(mock_chat_openai, config, mock_schema_explorer, mock_llm_response):
    # Mock the LLM response
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_llm_response
    
    with patch('langchain_core.prompts.ChatPromptTemplate') as mock_prompt:
        mock_prompt.return_value | mock_chat_openai.return_value | MagicMock.return_value = mock_chain
        
        generator = CypherQueryGenerator(config)
        query = generator.generate_query("Find all patents and their inventors")
        
        assert "MATCH (p:Patent)" in query
        assert "INVENTED_BY" in query
        assert "patent_number" in query
        assert "first_name" in query
        assert mock_chain.invoke.called

def test_generate_query_failure(config, mock_schema_explorer):
    generator = CypherQueryGenerator(config)
    
    # Mock the chain to raise an exception
    generator.query_chain.invoke = MagicMock(side_effect=Exception("Test error"))
    
    with pytest.raises(ValueError) as exc_info:
        generator.generate_query("Invalid question")
    
    assert "Failed to generate Cypher query" in str(exc_info.value)


