from typing import Dict, List, Any, Optional
import json

class ResearchPlanner:
    """
    Plans research strategies based on user queries.
    
    This component analyzes the research query, breaks it down into
    specific tasks, and creates a structured research plan.
    """
    
    def __init__(self, model):
        """
        Initialize the Research Planner.
        
        Args:
            model: The LLM model to use for planning
        """
        self.model = model
        self.system_prompt = """
        You are an expert research planner. Your task is to analyze a research query and develop
        a comprehensive research plan. Break down the query into specific research tasks that
        can be executed independently. Each task should be focused on a specific aspect of
        the research query.
        
        The research plan should be thorough and systematic, covering all important aspects of the
        query. Consider different perspectives, potential counterarguments, and relevant context.
        
        Your output should be in JSON format with the following structure:
        {
            "query_analysis": "A detailed analysis of the research query, identifying key themes and areas to explore",
            "context": "Important background information and context relevant to the query",
            "tasks": [
                "Task 1 description",
                "Task 2 description",
                ...
            ],
            "approach": "Overall approach to the research, including any specific methodologies or frameworks to use"
        }
        
        The tasks should be specific, actionable, and collectively cover all aspects needed to answer the query comprehensively.
        """
    
    async def create_research_plan(
        self, 
        query: str,
        existing_research: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive research plan for the given query.
        
        Args:
            query: The research query or topic
            existing_research: Any existing research on this topic
            
        Returns:
            A structured research plan
        """
        # Prepare the input for the model
        user_message = f"Research Query: {query}"
        
        # If we have existing research, include it for context
        if existing_research:
            existing_plan = existing_research.get("plan", {})
            existing_tasks = existing_plan.get("tasks", [])
            completed_tasks = [task for task in existing_tasks if task in existing_research.get("results", {})]
            
            if completed_tasks:
                tasks_str = "\n".join([f"- {task}" for task in completed_tasks])
                user_message += f"\n\nThe following tasks have already been completed:\n{tasks_str}\n\nPlease focus on new aspects or deeper analysis to complement the existing research."
        
        # Generate the research plan using the LLM
        response = await self.model.generate_response(
            system_prompt=self.system_prompt,
            user_message=user_message
        )
        
        # Parse the JSON response
        try:
            # Extract JSON from the response (handling potential text before/after the JSON)
            json_str = self._extract_json(response)
            research_plan = json.loads(json_str)
            
            # Ensure we have all required fields
            required_fields = ["query_analysis", "context", "tasks", "approach"]
            for field in required_fields:
                if field not in research_plan:
                    research_plan[field] = ""
            
            return research_plan
            
        except json.JSONDecodeError:
            # Fallback in case of parsing error
            return {
                "query_analysis": "Analysis of: " + query,
                "context": "General context for the query",
                "tasks": [
                    "Research basic information about " + query,
                    "Analyze key aspects of " + query,
                    "Investigate different perspectives on " + query,
                    "Summarize findings about " + query
                ],
                "approach": "Systematic research of available information"
            }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON object from text, handling cases where JSON is embedded in other text."""
        # Try to find JSON block starting with { and ending with }
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            return text[start_idx:end_idx+1]
        
        # If no JSON object found, return the original text
        return text
