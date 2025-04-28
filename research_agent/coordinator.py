import asyncio
from typing import Dict, List, Any, Optional
import json
import time

from research_agent.planner import ResearchPlanner
from research_agent.retriever import InformationRetriever
from research_agent.analyzer import ContentAnalyzer
from research_agent.report_generator import ReportGenerator
from research_agent.memory import ResearchMemory
from research_agent.models import FireworksModel

class ResearchCoordinator:
    """
    Coordinates the overall research process by managing specialized agents.
    
    This class directs the workflow between planning, information retrieval,
    content analysis, and report generation.
    """
    
    def __init__(
        self,
        fireworks_api_key: str,
        jina_api_key: Optional[str] = None,
        memory: Optional[ResearchMemory] = None,
        debug: bool = False
    ):
        self.debug = debug
        self.memory = memory or ResearchMemory()
        
        # Initialize model clients for different tasks with specific models
        # Using various models from fireworks.ai with different capabilities and costs
        self.planning_model = FireworksModel(
            api_key=fireworks_api_key,
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            temperature=0.2,
            max_tokens=4096,
            debug=debug
        )
        
        self.retrieval_model = FireworksModel(
            api_key=fireworks_api_key,
            model="accounts/fireworks/models/llama-v3p1-8b-instruct",
            temperature=0.1,
            max_tokens=2048,
            debug=debug
        )
        
        self.analysis_model = FireworksModel(
            api_key=fireworks_api_key,
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            temperature=0.3,
            max_tokens=4096,
            debug=debug
        )
        
        self.report_model = FireworksModel(
            api_key=fireworks_api_key,
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            temperature=0.2,
            max_tokens=8192,
            debug=debug
        )
        
        # Initialize specialized agents
        self.planner = ResearchPlanner(model=self.planning_model)
        self.retriever = InformationRetriever(
            model=self.retrieval_model, 
            jina_api_key=jina_api_key
        )
        self.analyzer = ContentAnalyzer(model=self.analysis_model)
        self.report_generator = ReportGenerator(model=self.report_model)
    
    async def conduct_research(
        self,
        query: str,
        session_id: str,
        response_handler: Any,
        plan_stream: Any
    ) -> Dict[str, Any]:
        """
        Conduct a comprehensive research process on the given query.
        
        Args:
            query: The research query or topic
            session_id: Identifier for the current session
            response_handler: Handler for streaming responses
            plan_stream: Stream for outputting the research plan
            
        Returns:
            Dictionary containing the research results and report
        """
        # Start timing the research process
        start_time = time.time()
        
        # Check if we have existing research for this query in memory
        existing_research = self.memory.get_research(session_id, query)
        if existing_research:
            # Emit a message about found existing research
            await response_handler.emit_text_block(
                "MEMORY_FOUND", 
                "Found existing research on this topic. Building upon previous findings."
            )
            # Add incremental plan to plan stream
            await plan_stream.emit_chunk(
                "Continuing previous research. Will supplement existing findings with new information.\n\n"
            )
        
        # Generate a research plan
        await plan_stream.emit_chunk("Analyzing query and developing a research plan...\n")
        research_plan = await self.planner.create_research_plan(query, existing_research)
        
        # Output the research plan
        plan_text = "\n".join([f"Task {i+1}: {task}" for i, task in enumerate(research_plan["tasks"])])
        await plan_stream.emit_chunk(f"\nResearch Plan:\n{plan_text}\n\n")
        
        # Initialize research results
        results = []
        
        # Execute each research task
        for i, task in enumerate(research_plan["tasks"]):
            task_number = i + 1
            task_key = f"TASK_{task_number}"
            
            # Notify about starting the task
            await response_handler.emit_text_block(
                task_key, 
                f"Working on Task {task_number}/{len(research_plan['tasks'])}: {task}"
            )
            await plan_stream.emit_chunk(f"Starting Task {task_number}: {task}...\n")
            
            # Retrieve information for this task
            await plan_stream.emit_chunk(f"Gathering information for task {task_number}...\n")
            retrieval_results = await self.retriever.retrieve_information(
                task, 
                research_plan["context"]
            )
            
            # Analyze the retrieved information
            await plan_stream.emit_chunk(f"Analyzing information for task {task_number}...\n")
            analysis = await self.analyzer.analyze_content(
                task,
                retrieval_results,
                research_plan["context"]
            )
            
            # Store the results
            results.append({
                "task": task,
                "retrieval_results": retrieval_results,
                "analysis": analysis
            })
            
            # Emit the analysis result
            summary = analysis.get("summary", "No summary available")
            await response_handler.emit_text_block(
                f"{task_key}_RESULT", 
                f"Task {task_number} Findings: {summary}"
            )
            
            # Update the plan stream
            await plan_stream.emit_chunk(f"✓ Completed Task {task_number}\n\n")
            
            # Store in memory
            self.memory.update_task_result(session_id, query, task, {
                "retrieval_results": retrieval_results,
                "analysis": analysis
            })
        
        # Generate the comprehensive research report
        await response_handler.emit_text_block(
            "GENERATING_REPORT", 
            "All research tasks completed. Generating comprehensive report..."
        )
        await plan_stream.emit_chunk("Synthesizing findings into comprehensive report...\n")
        
        report = await self.report_generator.generate_report(
            query,
            research_plan,
            results
        )
        
        # Calculate and add timing information
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        timing_info = f"Research completed in {minutes} minutes and {seconds} seconds."
        
        # Store the complete research in memory
        self.memory.store_research(session_id, query, {
            "query": query,
            "plan": research_plan,
            "results": results,
            "report": report,
            "timing": timing_info
        })
        
        # Return the research results
        return {
            "query": query,
            "plan": research_plan,
            "results": results,
            "report": report,
            "timing": timing_info
        }
