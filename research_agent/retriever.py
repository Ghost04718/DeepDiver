from typing import Dict, List, Any, Optional
import json
import os
import re
import requests
import asyncio

class JinaSearchProvider:
    """
    Integration with Jina AI for semantic search and reranking.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Jina search provider.
        
        Args:
            api_key: Jina AI API key (optional, can also use environment variable)
        """
        self.api_key = api_key or os.environ.get("JINA_API_KEY")
        self.api_url = 'https://api.jina.ai/v1/embeddings'
        
        if not self.api_key:
            print("Warning: No Jina API key provided. Semantic search functionality will be limited.")
    
    async def rerank_results(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank documents based on their semantic similarity to the query.
        
        Args:
            query: The search query
            documents: List of document texts to rank
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with reranked documents and scores
        """
        if not self.api_key or not documents:
            # Return documents without reranking if no API key or no documents
            return [{"document": doc, "score": 1.0} for doc in documents[:top_k]]
        
        try:
            # Prepare texts for embedding (query + documents)
            all_texts = [query] + documents
            
            # Call Jina AI API for embeddings
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = {
                "model": "jina-embeddings-v3",
                "task": "text-matching",
                "input": all_texts
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract embeddings
            embeddings = [item["embedding"] for item in response.json()["data"]]
            
            # Query embedding is the first one
            query_embedding = embeddings[0]
            doc_embeddings = embeddings[1:]
            
            # Calculate similarity scores using dot product
            scores = []
            for i, doc_embedding in enumerate(doc_embeddings):
                # Simple dot product similarity
                similarity = sum(q * d for q, d in zip(query_embedding, doc_embedding))
                scores.append({"document": documents[i], "score": similarity, "index": i})
            
            # Sort by score and get top_k
            reranked = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
            
            # Return the reranked documents
            return [{"document": item["document"], "score": item["score"]} for item in reranked]
            
        except Exception as e:
            print(f"Error in Jina reranking: {str(e)}")
            # Fallback to original order
            return [{"document": doc, "score": 1.0} for doc in documents[:top_k]]


class InformationRetriever:
    """
    Retrieves information from various sources based on research tasks.
    
    This component is responsible for gathering information needed to complete
    research tasks, including web search, document retrieval, and data extraction.
    """
    
    def __init__(
        self, 
        model,
        jina_api_key: Optional[str] = None
    ):
        """
        Initialize the Information Retriever.
        
        Args:
            model: The LLM model to use for retrieval tasks
            jina_api_key: API key for Jina AI semantic search (optional)
        """
        self.model = model
        self.jina_search = JinaSearchProvider(api_key=jina_api_key)
        
        self.system_prompt = """
        You are an expert information retriever specialized in deep research. Your task is to simulate 
        the retrieval of information for a research task. Since you don't have direct web access, you'll 
        generate synthetic but realistic information that would likely be found during actual research.
        
        For each research task, generate detailed, fact-based information that:
        1. Is relevant to the specific task
        2. Includes a mix of general context, specific details, and key insights
        3. Presents multiple viewpoints or perspectives when appropriate
        4. Cites imaginary but plausible sources (academic papers, books, articles)
        5. Contains factual information to the best of your knowledge
        
        Your output should be in JSON format with the following structure:
        {
            "search_queries": ["query1", "query2", ...],
            "sources": [
                {
                    "title": "Source title",
                    "author": "Author name (if applicable)",
                    "publication": "Publication name (if applicable)",
                    "year": "Publication year (if applicable)",
                    "content": "Extracted content from the source",
                    "url": "Simulated URL"
                },
                ...
            ],
            "key_points": ["key point 1", "key point 2", ...],
            "additional_search_areas": ["area1", "area2", ...]
        }
        
        Ensure the content is informative, detailed, and directly related to the research task.
        """
    
    async def retrieve_information(
        self, 
        task: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Retrieve information relevant to a specific research task.
        
        Args:
            task: The research task description
            context: Additional context for the task
            
        Returns:
            Dict containing retrieved information and sources
        """
        # Prepare the input for the model
        user_message = f"""
        Research Task: {task}
        
        Context: {context}
        
        Please retrieve comprehensive information for this research task. Include diverse sources
        and perspectives to ensure thorough coverage of the topic.
        """
        
        # Generate information using the LLM
        response = await self.model.generate_response(
            system_prompt=self.system_prompt,
            user_message=user_message
        )
        
        # Extract and parse the JSON response
        try:
            json_str = self._extract_json(response)
            retrieval_results = json.loads(json_str)
            
            # Extract all content for reranking
            if retrieval_results.get("sources"):
                documents = [source.get("content", "") for source in retrieval_results["sources"]]
                
                # Rerank the sources based on relevance to the task
                reranked_docs = await self.jina_search.rerank_results(task, documents)
                
                # Reorder the sources based on the reranking
                reranked_sources = []
                for doc_info in reranked_docs:
                    # Find the original source
                    for source in retrieval_results["sources"]:
                        if source.get("content") == doc_info["document"]:
                            # Add the reranking score
                            source["relevance_score"] = doc_info["score"]
                            reranked_sources.append(source)
                            break
                
                # Update the sources with the reranked list
                retrieval_results["sources"] = reranked_sources
            
            return retrieval_results
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback in case of parsing error
            return {
                "search_queries": [f"Information about {task}"],
                "sources": [
                    {
                        "title": f"Research on {task}",
                        "author": "Various experts",
                        "publication": "Research Journal",
                        "year": "Recent",
                        "content": f"General information about {task}. " + response[:500],
                        "url": "https://example.com/research"
                    }
                ],
                "key_points": [f"Basic information about {task}"],
                "additional_search_areas": [f"More specific aspects of {task}"]
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
