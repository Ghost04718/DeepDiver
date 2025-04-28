from typing import Dict, List, Any
import json

class ReportGenerator:
    """
    Synthesizes research findings into comprehensive, structured reports.
    
    This component takes the results of all research tasks and creates a
    cohesive, well-organized research report that addresses the original query.
    """
    
    def __init__(self, model):
        """
        Initialize the Report Generator.
        
        Args:
            model: The LLM model to use for report generation
        """
        self.model = model
        self.system_prompt = """
        You are an expert research report writer. Your task is to synthesize the findings from multiple
        research tasks into a comprehensive, well-structured research report. The report should directly
        address the original research query with thorough, nuanced analysis.

        Your report should:
        1. Begin with an executive summary that concisely answers the research query
        2. Include a structured breakdown of key findings organized by theme or topic
        3. Present evidence and insights from all research tasks
        4. Acknowledge different perspectives, contradictions, and uncertainties
        5. Include citations to sources where appropriate
        6. End with clear conclusions and recommendations (if applicable)
        
        Format the report professionally with:
        - Clear section headings and subheadings
        - Well-structured paragraphs
        - Bullet points for lists and key points
        - Citations in a consistent format
        - Professional, academic tone
        
        Make the report thorough and comprehensive while remaining focused on the original query.
        """
    
    async def generate_report(
        self, 
        query: str,
        research_plan: Dict[str, Any],
        task_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive research report.
        
        Args:
            query: The original research query
            research_plan: The plan used to guide the research
            task_results: Results from all individual research tasks
            
        Returns:
            A formatted research report as a string
        """
        # Extract task analyses from results
        tasks_summary = ""
        for i, result in enumerate(task_results):
            task = result.get("task", f"Task {i+1}")
            analysis = result.get("analysis", {})
            summary = analysis.get("summary", "No summary available")
            
            tasks_summary += f"\nTASK {i+1}: {task}\n"
            tasks_summary += f"Summary: {summary}\n"
            
            # Add key insights
            key_insights = analysis.get("key_insights", [])
            if key_insights:
                tasks_summary += "Key Insights:\n"
                for insight in key_insights:
                    insight_text = insight.get("insight", "")
                    confidence = insight.get("confidence", "")
                    if insight_text:
                        tasks_summary += f"- {insight_text} (Confidence: {confidence})\n"
            
            # Add information gaps
            info_gaps = analysis.get("information_gaps", [])
            if info_gaps:
                tasks_summary += "Information Gaps:\n"
                for gap in info_gaps:
                    tasks_summary += f"- {gap}\n"
        
        # Extract sources for citations
        all_sources = []
        for result in task_results:
            retrieval_results = result.get("retrieval_results", {})
            sources = retrieval_results.get("sources", [])
            all_sources.extend(sources)
        
        sources_text = ""
        for i, source in enumerate(all_sources):
            sources_text += f"\nSOURCE {i+1}:\n"
            sources_text += f"Title: {source.get('title', 'Untitled')}\n"
            sources_text += f"Author: {source.get('author', 'Unknown')}\n"
            sources_text += f"Publication: {source.get('publication', 'N/A')}\n"
            sources_text += f"Year: {source.get('year', 'N/A')}\n"
            sources_text += f"URL: {source.get('url', 'No URL available')}\n"
        
        # Prepare the input for the model
        user_message = f"""
        Research Query: {query}
        
        Query Analysis: {research_plan.get("query_analysis", "")}
        
        Research Approach: {research_plan.get("approach", "")}
        
        Task Results:
        {tasks_summary}
        
        Available Sources for Citations:
        {sources_text}
        
        Please synthesize this information into a comprehensive research report that thoroughly
        addresses the original query. The report should be well-structured with clear sections,
        include citations to sources where appropriate, and provide nuanced analysis that
        acknowledges different perspectives and limitations of the research.
        """
        
        # Generate the report using the LLM
        report = await self.model.generate_response(
            system_prompt=self.system_prompt,
            user_message=user_message
        )
        
        return report
