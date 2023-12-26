import os
import numpy as np
from langchain.graphs import Neo4jGraph

def get_current_wait_times(hospital: str) -> str | float:
    
    """ TODO """
    
    graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"))
    
    current_hospitals = graph.query("""
                                    MATCH (h:Hospital)
                                    RETURN h.name AS hospital_name 
                                    """)
    
    current_hospitals = [d["hospital_name"].lower() for d in current_hospitals]
    
    if hospital.lower() not in current_hospitals:
        
        return f"Hospital '{hospital}' does not exist"
    
    return np.random.randint(low=0, high=600)