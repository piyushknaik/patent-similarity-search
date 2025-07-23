from pydantic_settings import BaseSettings
from neo4j import GraphDatabase
from typing import Optional
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jSettings(BaseSettings):
    """Settings for Neo4j database connection."""
    uri: str = os.getenv("NEO4J_URI")
    username: str = os.getenv("NEO4J_USERNAME")
    password: str = os.getenv("NEO4J_PASSWORD")
    database: str = os.getenv("NEO4J_DATABASE", "neo4j")

class Neo4jConnection:
    """Neo4j database connection manager."""
    
    def __init__(self):
        self.settings = Neo4jSettings()
        self._driver = None

    @property
    def driver(self):
        """Lazy initialization of the Neo4j driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.settings.uri,
                auth=(self.settings.username, self.settings.password)
            )
        return self._driver

    def verify_connectivity(self):
        """Verify the connection to Neo4j database."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {str(e)}")
            return False

    def close(self):
        """Close the database connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

def with_neo4j_connection(func):
    """Decorator to handle Neo4j connection."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Neo4jConnection() as conn:
            return func(conn, *args, **kwargs)
    return wrapper
