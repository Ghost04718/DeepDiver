from typing import Dict, List, Any, Optional
import json
import re
import time

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from a text string.
    
    Args:
        text: Text that may contain a JSON object
        
    Returns:
        Extracted JSON object as a dictionary, or empty dict if extraction fails
    """
    # Find JSON-like patterns (objects starting with { and ending with })
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try a more aggressive approach if the first method fails
    try:
        # Find the first { and the last }
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_str = text[start_idx:end_idx+1]
            return json.loads(json_str)
    except (json.JSONDecodeError, Exception):
        pass
    
    # Return empty dict if all extraction attempts fail
    return {}

def format_research_plan(plan: Dict[str, Any]) -> str:
    """
    Format a research plan into a readable string.
    
    Args:
        plan: Research plan dictionary
        
    Returns:
        Formatted plan as a string
    """
    formatted_plan = "# Research Plan\n\n"
    
    # Add query analysis
    if "query_analysis" in plan:
        formatted_plan += "## Query Analysis\n"
        formatted_plan += plan["query_analysis"] + "\n\n"
    
    # Add context
    if "context" in plan:
        formatted_plan += "## Context\n"
        formatted_plan += plan["context"] + "\n\n"
    
    # Add tasks
    if "tasks" in plan:
        formatted_plan += "## Research Tasks\n"
        for i, task in enumerate(plan["tasks"]):
            formatted_plan += f"{i+1}. {task}\n"
        formatted_plan += "\n"
    
    # Add approach
    if "approach" in plan:
        formatted_plan += "## Research Approach\n"
        formatted_plan += plan["approach"] + "\n\n"
    
    return formatted_plan

def format_source_citation(source: Dict[str, Any]) -> str:
    """
    Format a source as a citation string.
    
    Args:
        source: Source dictionary
        
    Returns:
        Formatted citation string
    """
    title = source.get("title", "Untitled")
    author = source.get("author", "Unknown")
    publication = source.get("publication", "")
    year = source.get("year", "")
    url = source.get("url", "")
    
    citation = f"{title}"
    
    if author != "Unknown":
        citation += f", by {author}"
    
    if publication:
        citation += f", in {publication}"
    
    if year:
        citation += f" ({year})"
    
    if url:
        citation += f" [Available at: {url}]"
    
    return citation

def format_time_elapsed(start_time: float) -> str:
    """
    Format elapsed time into a readable string.
    
    Args:
        start_time: Start time in seconds (from time.time())
        
    Returns:
        Formatted time string
    """
    elapsed = time.time() - start_time
    
    # Format as hours, minutes, seconds
    hours, remainder = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def chunk_text(text: str, chunk_size: int = 100) -> List[str]:
    """
    Split text into chunks of specified size.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    # Split at sentence boundaries where possible
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk size, start a new chunk
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk if there's anything left
    if current_chunk:
        chunks.append(current_chunk)
    
    # If any chunk is still larger than chunk_size, split it further
    result = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            result.append(chunk)
        else:
            # Split the chunk at chunk_size boundaries
            result.extend([chunk[i:i+chunk_size] for i in range(0, len(chunk), chunk_size)])
    
    return result
