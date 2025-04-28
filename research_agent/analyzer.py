from typing import Dict, List, Any, Optional
import json

class ContentAnalyzer:
    """
    Analyzes retrieved content to extract insights and key information.
    
    This component processes the raw information gathered by the retriever,
    identifies patterns, extracts key insights, and evaluates the quality
    and relevance of the information.
    """
    
    def __init__(self, model):
        """
        Initialize the Content Analyzer.
        
        Args:
            model: The LLM model to use for analysis
        """
        self.model = model
        self.system_prompt = """
        You are an expert content analyst specializing in research synthesis. Your task is to analyze
        information retrieved for a research task and extract key insights, patterns, and conclusions.
        
        Analyze the information with:
        1. Critical evaluation of source quality and relevance
        2. Identification of key themes, patterns, and trends
        3. Extraction of important facts, statistics, and quotes
        4. Recognition of differing perspectives and potential biases
        5. Assessment of information gaps or areas needing further research
        
        Your output should be in JSON format with the following structure:
        {
            "summary": "A concise summary of the key findings",
            "key_insights": [
                {"insight": "Description of insight", "confidence": "high/medium/low", "supporting_evidence": "Evidence that supports this insight"},
                ...
            ],
            "themes": [
                {"theme": "Theme name", "description": "Description of the theme"},
                ...
            ],
            "contradictions": [
                {"description": "Description of the contradiction", "perspective1": "First perspective", "perspective2": "Second perspective"},
                ...
            ],
            "information_gaps": ["Gap 1", "Gap 2", ...],
            "quality_assessment": {
                "overall_quality": "high/medium/low",
                "explanation": "Explanation of quality assessment",
                "most_credible_sources": ["Source 1", "Source 2", ...],
                "questionable_sources": ["Source 1", "Source 2", ...]
            }
        }
        
        Be thorough, critical, and nuanced in your analysis.
        """
    
    async def analyze_content(
        self, 
        task: str,
        retrieval_results: Dict[str, Any],
        context: str
    ) -> Dict[str, Any]:
        """
        Analyze the content retrieved for a research task.
        
        Args:
            task: The research task description
            retrieval_results: The information retrieved for the task
            context: Additional context about the research
            
        Returns:
            Dict containing analysis results
        """
        # Extract sources from retrieval results
        sources = retrieval_results.get("sources", [])
        sources_text = ""
        
        for i, source in enumerate(sources):
            sources_text += f"\nSOURCE {i+1}:\n"
            sources_text += f"Title: {source.get('title', 'Untitled')}\n"
            sources_text += f"Author: {source.get('author', 'Unknown')}\n"
            sources_text += f"Publication: {source.get('publication', 'N/A')}\n"
            sources_text += f"Year: {source.get('year', 'N/A')}\n"
            sources_text += f"Content: {source.get('content', 'No content available')}\n"
            sources_text += f"URL: {source.get('url', 'No URL available')}\n"
        
        # Extract key points
        key_points = retrieval_results.get("key_points", [])
        key_points_text = "\nKEY POINTS:\n" + "\n".join([f"- {point}" for point in key_points])
        
        # Prepare the input for the model
        user_message = f"""
        Research Task: {task}
        
        Context: {context}
        
        Retrieved Information:
        {sources_text}
        {key_points_text}
        
        Please analyze this information thoroughly to extract key insights, identify themes,
        note contradictions, and assess the quality of the information.
        """
        
        # Generate analysis using the LLM
        response = await self.model.generate_response(
            system_prompt=self.system_prompt,
            user_message=user_message
        )
        
        # Extract and parse the JSON response
        try:
            json_str = self._extract_json(response)
            analysis_results = json.loads(json_str)
            return analysis_results
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback in case of parsing error
            return {
                "summary": f"Analysis of information related to {task}.",
                "key_insights": [
                    {
                        "insight": "The information provides a general overview of the topic.",
                        "confidence": "medium",
                        "supporting_evidence": "Multiple sources cover the basic aspects of the topic."
                    }
                ],
                "themes": [
                    {
                        "theme": "General information",
                        "description": "Basic background information about the topic."
                    }
                ],
                "contradictions": [],
                "information_gaps": ["More specific details needed"],
                "quality_assessment": {
                    "overall_quality": "medium",
                    "explanation": "The information is generally relevant but could be more comprehensive.",
                    "most_credible_sources": [],
                    "questionable_sources": []
                }
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
