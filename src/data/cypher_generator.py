import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Third-party imports
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_models import ChatOpenAI

# Local imports
from ..database.neo4j_schema import Neo4jSchemaExplorer, GraphSchema
from ..database.neo4j_connection import Neo4jConnection

# Load environment variables
load_dotenv()

class CypherQuery(BaseModel):
    """Pydantic model for Cypher query output."""
    query: str = Field(
        description="Cypher query to retrieve information from the graph database."
    )

@dataclass
class QueryGeneratorConfig:
    """Configuration for the QueryGenerator."""
    model_name: str = os.getenv("LLM_MODEL_NAME")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    api_key: str = os.getenv("LLM_API_KEY")
    api_base: str = os.getenv("LLM_API_BASE")

    @classmethod
    def from_env(cls) -> 'QueryGeneratorConfig':
        """
        Create a configuration instance from environment variables.
        
        Returns:
            QueryGeneratorConfig: Configuration instance with values from environment.
        
        Raises:
            ValueError: If required environment variables are missing.
        """
        if not os.getenv("LLM_API_KEY"):
            raise ValueError("LLM_API_KEY environment variable is required")
        return cls()

class CypherQueryGenerator:
    """Class for generating Cypher queries from natural language using LLM."""

    def __init__(self, config: Optional[QueryGeneratorConfig] = None):
        """
        Initialize the query generator.

        Args:
            config (Optional[QueryGeneratorConfig]): Configuration for the LLM.
                                                   If None, loads from environment variables.
        """
        self.config = config if config is not None else QueryGeneratorConfig.from_env()
        self.llm = self._initialize_llm()
        self.schema_explorer = Neo4jSchemaExplorer()
        self.parser = JsonOutputParser(pydantic_object=CypherQuery)
        self.prompt = self._create_prompt_template()
        self.query_chain = self.prompt | self.llm | self.parser

    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model."""
        return ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            openai_api_key=self.config.api_key,
            openai_api_base=self.config.api_base
        )

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for query generation."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a Neo4j expert. Given the following user question and graph schema,
             generate a Cypher query to answer the question.
             Output the answer as a JSON object containing Patent related_patent_number, 
             patent_title, inventor_first_name and inventor_last_name
             and with a single key 'query' that contains the Cypher query string.
             
             Graph Schema:
             {schema}
             """),
            ("human", "{question}")
        ])

    def _format_schema(self, schema: GraphSchema) -> str:
        """
        Format the graph schema for the prompt.

        Args:
            schema (GraphSchema): The Neo4j graph schema.

        Returns:
            str: Formatted schema string.
        """
        schema_parts = []
        
        # Add node labels
        schema_parts.append("Node Labels:")
        for label in schema.node_labels:
            schema_parts.append(f"- {label}")
        
        # Add relationship types
        schema_parts.append("\nRelationship Types:")
        for rel_type in schema.relationship_types:
            schema_parts.append(f"- {rel_type}")
        
        # Add property keys
        schema_parts.append("\nProperty Keys:")
        for prop_key in schema.property_keys:
            schema_parts.append(f"- {prop_key}")
        
        return "\n".join(schema_parts)

    def generate_query(self, question: str) -> str:
        """
        Generate a Cypher query from a natural language question.

        Args:
            question (str): The natural language question.

        Returns:
            str: The generated Cypher query.

        Raises:
            ConnectionError: If unable to connect to Neo4j database.
            ValueError: If query generation fails.
        """
        try:
            # Get the current schema
            schema = self.schema_explorer.get_schema()
            formatted_schema = self._format_schema(schema)

            # Generate the query
            response = self.query_chain.invoke({
                "question": question,
                "schema": formatted_schema
            })

            return response.query

        except Exception as e:
            raise ValueError(f"Failed to generate Cypher query: {str(e)}")
            
    def execute_cypher_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query against the Neo4j database.

        Args:
            query (str): The Cypher query string.

        Returns:
            List[Dict[str, Any]]: The results of the query as a list of dictionaries.
            
        Raises:
            ConnectionError: If unable to connect to Neo4j database.
            ValueError: If query execution fails.
        """
        try:
            with Neo4jConnection() as connection:
                results = connection.query(query)
                return results
        except Exception as e:
            raise ValueError(f"Failed to execute Cypher query: {str(e)}")
