from neo4j import GraphDatabase
from django.conf import settings


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_CONNECTION['URI'],
            auth=(
                settings.NEO4J_CONNECTION['USERNAME'],
                settings.NEO4J_CONNECTION['PASSWORD']
            )
        )

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        with self.driver.session() as session:
            query = (
                f"CREATE (n:{label} $properties) "
                "RETURN n"
            )
            result = session.run(query, properties=properties)
            return result.single()

    def get_node(self, label, property_name, property_value):
        with self.driver.session() as session:
            query = (
                f"MATCH (n:{label}) "
                f"WHERE n.{property_name} = $value "
                "RETURN n"
            )
            result = session.run(query, value=property_value)
            return result.single()

    def create_relationship(self, from_user_id, to_user_id, relationship_type):
        with self.driver.session() as session:
            query = (
                "MERGE (a:User {id: $from_user_id}) "
                "MERGE (b:User {id: $to_user_id}) "
                f"CREATE (a)-[r:{relationship_type}]->(b) "
                "RETURN r"
            )
            try:
                result = session.run(query, from_user_id=from_user_id, to_user_id=to_user_id)
                created_relationship = result.single()
                
                if created_relationship:
                    print("Relationship created:", created_relationship)
                else:
                    print("No relationship was created.")
                
                return created_relationship
            
            except Exception as e:
                print(f"Error creating relationship: {e}")
                return None

    def delete_relationship(self, from_user_id, to_user_id):
        print(from_user_id, to_user_id)
        with self.driver.session() as session:
            query = (
                "MATCH (a:User {id: $from_user_id})-[r:FOLLOWS]->(b:User {id: $to_user_id}) "
                "DELETE r "
                "RETURN r"
            )
            try:

                result = session.run(query, from_user_id=from_user_id, to_user_id=to_user_id)
                            # Fetch all data to ensure visibility into the results
                data = result.data()

                if data:
                    print(f"Deleted relationship data: {data}")
                    return data  # Return the deleted relationship details
                else:
                    print(f"No relationship found to delete between {from_user_id} and {to_user_id}.")
                    return None
            except Exception as e:
                print(f"Error deleting relationship: {e}")
                return None


    # def print_connected_nodes(self, user_id, level):
    #     print(user_id)
    #     with self.driver.session() as session:
    #         query = (
    #             "MATCH (u:User {id: $user_id}) "
    #             "CALL apoc.path.subgraphNodes(u, {maxLevel: $level}) YIELD node "
    #             "RETURN node"
    #         )
    #         try:
    #             result = session.run(query, user_id=user_id, level=level)
    #             connected_nodes = result.data()
                
    #             if connected_nodes:
    #                 print(f"Connected nodes for user {user_id} up to level {level}:")
    #                 # for record in connected_nodes:
    #                 #     print(record['node'])
    #                 nodes = [record['node'] for record in connected_nodes]
    #                 return nodes
    #             else:
    #                 print(f"No connected nodes found for user {user_id}.")
                
    #         except Exception as e:
    #             print(f"Error fetching connected nodes: {e}")
    def print_connected_nodes(self, user_id, level):
        print(user_id)
        with self.driver.session() as session:
            query = (
                "MATCH (u:User {id: $user_id}) "
                "CALL apoc.path.subgraphNodes(u, {maxLevel: $level}) YIELD node "
                "RETURN node"
            )
            try:
                result = session.run(query, user_id=user_id, level=level)
                connected_nodes = result.data()

                if connected_nodes:
                    print(f"Connected nodes for user {user_id} up to level {level}:")
                    nodes = [record['node'] for record in connected_nodes]
                    return nodes
                else:
                    print(f"No connected nodes found for user {user_id}.")
                    return []

            except Exception as e:
                print(f"Error fetching connected nodes: {e}")
                return []
