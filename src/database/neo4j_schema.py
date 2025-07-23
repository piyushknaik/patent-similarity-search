from typing import Dict, List
from dataclasses import dataclass
from src.database.neo4j_connection import Neo4jConnection, with_neo4j_connection

@dataclass
class GraphSchema:
    """Data class to hold graph schema information."""
    node_labels: List[str]
    relationship_types: List[str]
    property_keys: List[str]

    def display(self):
        """Display the schema information in a formatted way."""
        print("Node Labels:")
        for label in self.node_labels:
            print(f"- {label}")

        print("\nRelationship Types:")
        for rel_type in self.relationship_types:
            print(f"- {rel_type}")

        print("\nProperty Keys (across all nodes and relationships):")
        for prop_key in self.property_keys:
            print(f"- {prop_key}")

class Neo4jSchemaExplorer:
    """Class for exploring and displaying Neo4j schema information."""

    def __init__(self):
        self._connection = Neo4jConnection()

    def _get_schema(self, session):
        """
        Retrieves schema information from the Neo4j database.

        Args:
            session: Neo4j session object.

        Returns:
            GraphSchema: Object containing schema information.
        """
        # Get node labels
        node_labels = session.run("CALL db.labels()").data()
        labels = [item['label'] for item in node_labels] if node_labels else []

        # Get relationship types
        relationship_types = session.run("CALL db.relationshipTypes()").data()
        rel_types = [item['relationshipType'] for item in relationship_types] if relationship_types else []

        # Get property keys
        property_keys = session.run("CALL db.propertyKeys()").data()
        prop_keys = [item['propertyKey'] for item in property_keys] if property_keys else []

        return GraphSchema(
            node_labels=labels,
            relationship_types=rel_types,
            property_keys=prop_keys
        )

    def get_schema(self) -> GraphSchema:
        """
        Get the complete schema of the Neo4j database.

        Returns:
            GraphSchema: Object containing schema information.
            
        Raises:
            ConnectionError: If unable to connect to the database.
        """
        with self._connection as conn:
            if not conn.verify_connectivity():
                raise ConnectionError("Failed to connect to Neo4j database")
            
            with conn.driver.session() as session:
                return self._get_schema(session)

    def get_node_properties(self, label: str) -> Dict[str, List[str]]:
        """
        Get properties for a specific node label.

        Args:
            label: The node label to get properties for.

        Returns:
            Dict containing property information for the specified node label.

        Raises:
            ConnectionError: If unable to connect to the database.
        """
        query = """
        MATCH (n:`{label}`)
        WITH DISTINCT keys(n) as keys
        UNWIND keys as key
        RETURN DISTINCT key
        """.replace("{label}", label)

        with self._connection as conn:
            if not conn.verify_connectivity():
                raise ConnectionError("Failed to connect to Neo4j database")
            
            with conn.driver.session() as session:
                result = session.run(query).data()
                return {label: [item['key'] for item in result] if result else []}

    def get_relationship_properties(self, rel_type: str) -> Dict[str, List[str]]:
        """
        Get properties for a specific relationship type.

        Args:
            rel_type: The relationship type to get properties for.

        Returns:
            Dict containing property information for the specified relationship type.

        Raises:
            ConnectionError: If unable to connect to the database.
        """
        query = """
        MATCH ()-[r:`{rel_type}`]->()
        WITH DISTINCT keys(r) as keys
        UNWIND keys as key
        RETURN DISTINCT key
        """.replace("{rel_type}", rel_type)

        with self._connection as conn:
            if not conn.verify_connectivity():
                raise ConnectionError("Failed to connect to Neo4j database")
            
            with conn.driver.session() as session:
                result = session.run(query).data()
                return {rel_type: [item['key'] for item in result] if result else []}
