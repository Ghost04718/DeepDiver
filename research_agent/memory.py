from typing import Dict, List, Any, Optional
import json

class ResearchMemory:
    """
    Manages state and memory for research sessions.
    
    This component stores research results, tracks the research process,
    and enables persistency across interactions.
    """
    
    def __init__(self):
        """Initialize the Research Memory system."""
        # Dictionary to store research information by session and query
        # Structure: {session_id: {query: research_data}}
        self.research_store = {}
        
        # Dictionary to store task results by session, query, and task
        # Structure: {session_id: {query: {task: task_result}}}
        self.task_store = {}
    
    def store_research(self, session_id: str, query: str, research_data: Dict[str, Any]) -> None:
        """
        Store research data for a session and query.
        
        Args:
            session_id: Identifier for the session
            query: The research query
            research_data: Data to store
        """
        # Initialize session if needed
        if session_id not in self.research_store:
            self.research_store[session_id] = {}
        
        # Store the research data
        self.research_store[session_id][query] = research_data
    
    def get_research(self, session_id: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve research data for a session and query.
        
        Args:
            session_id: Identifier for the session
            query: The research query
            
        Returns:
            The stored research data, or None if not found
        """
        return self.research_store.get(session_id, {}).get(query)
    
    def update_task_result(
        self, 
        session_id: str, 
        query: str, 
        task: str, 
        result: Dict[str, Any]
    ) -> None:
        """
        Store or update the result of a research task.
        
        Args:
            session_id: Identifier for the session
            query: The research query
            task: The specific research task
            result: The task result data
        """
        # Initialize dictionaries if needed
        if session_id not in self.task_store:
            self.task_store[session_id] = {}
        
        if query not in self.task_store[session_id]:
            self.task_store[session_id][query] = {}
        
        # Store the task result
        self.task_store[session_id][query][task] = result
    
    def get_task_result(
        self, 
        session_id: str, 
        query: str, 
        task: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve the result of a research task.
        
        Args:
            session_id: Identifier for the session
            query: The research query
            task: The specific research task
            
        Returns:
            The stored task result, or None if not found
        """
        return self.task_store.get(session_id, {}).get(query, {}).get(task)
    
    def get_all_task_results(
        self, 
        session_id: str, 
        query: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all task results for a session and query.
        
        Args:
            session_id: Identifier for the session
            query: The research query
            
        Returns:
            Dictionary mapping tasks to their results
        """
        return self.task_store.get(session_id, {}).get(query, {})
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all stored data for a session.
        
        Args:
            session_id: Identifier for the session to clear
        """
        if session_id in self.research_store:
            del self.research_store[session_id]
        
        if session_id in self.task_store:
            del self.task_store[session_id]
    
    def serialize(self) -> str:
        """
        Serialize all memory data to a JSON string.
        
        Returns:
            JSON string representation of the memory state
        """
        data = {
            "research_store": self.research_store,
            "task_store": self.task_store
        }
        return json.dumps(data)
    
    def deserialize(self, data_str: str) -> None:
        """
        Load memory state from a JSON string.
        
        Args:
            data_str: JSON string representation of memory state
        """
        try:
            data = json.loads(data_str)
            self.research_store = data.get("research_store", {})
            self.task_store = data.get("task_store", {})
        except json.JSONDecodeError:
            print("Error deserializing memory data: Invalid JSON format")
