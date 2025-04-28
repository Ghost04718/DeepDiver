from sentient_agent_framework import AbstractAgent, Session, Query, ResponseHandler
import os
import json
import asyncio
from typing import Dict, List, Any, Optional

class DeepResearchAgent(AbstractAgent):
    """
    Deep Research Agent for Sentient Chat
    
    This agent coordinates a multi-agent research system to deliver comprehensive
    research reports on complex topics. It manages multiple specialized sub-agents
    to break down research tasks, gather information, analyze content, and 
    synthesize findings into detailed reports.
    """
    
    def __init__(
        self,
        name: str = "Deep Research Agent",
        fireworks_api_key: Optional[str] = None,
        jina_api_key: Optional[str] = None,
        debug: bool = False
    ):
        super().__init__(name)
        
        # Set API keys (from parameters or environment variables)
        self.fireworks_api_key = fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
        if not self.fireworks_api_key:
            raise ValueError("Fireworks API key is required. Provide it as a parameter or set FIREWORKS_API_KEY environment variable.")
            
        self.jina_api_key = jina_api_key or os.environ.get("JINA_API_KEY")
        
        # Debug mode for additional logging
        self.debug = debug
        
        # Initialize component managers
        from research_agent.coordinator import ResearchCoordinator
        from research_agent.memory import ResearchMemory
        
        self.memory = ResearchMemory()
        self.coordinator = ResearchCoordinator(
            fireworks_api_key=self.fireworks_api_key,
            jina_api_key=self.jina_api_key,
            memory=self.memory,
            debug=self.debug
        )
        
    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """
        Process the user's research query and generate a comprehensive response.
        
        Args:
            session: The current session information
            query: User's research query
            response_handler: Handler for sending responses back to the client
        """
        # Log the incoming query if in debug mode
        if self.debug:
            print(f"Received query: {query.prompt}")
        
        # Start the response with a greeting and acknowledgment
        await response_handler.emit_text_block(
            "GREETING", 
            f"I'm your Deep Research Assistant. Starting comprehensive research on: '{query.prompt}'"
        )
        
        # Create a stream for the research plan
        plan_stream = response_handler.create_text_stream("RESEARCH_PLAN")
        
        # Perform the research using the coordinator
        research_result = await self.coordinator.conduct_research(
            query.prompt,
            session_id=str(session.activity_id),
            response_handler=response_handler,
            plan_stream=plan_stream
        )
        
        # Mark the research plan stream as complete
        await plan_stream.complete()
        
        # Create a stream for the final response
        final_response_stream = response_handler.create_text_stream("FINAL_REPORT")
        
        # Stream the final research report
        report_chunks = self._chunk_text(research_result["report"], chunk_size=100)
        for chunk in report_chunks:
            await final_response_stream.emit_chunk(chunk)
            await asyncio.sleep(0.05)  # Small delay for realistic streaming
            
        # Mark the final response stream as complete
        await final_response_stream.complete()
        
        # Complete the overall response
        await response_handler.complete()
    
    def _chunk_text(self, text: str, chunk_size: int = 100) -> List[str]:
        """Break text into chunks for streaming."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
