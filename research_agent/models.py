from typing import Dict, List, Any, Optional
import os
import json
import httpx
import asyncio
import time

class FireworksModel:
    """
    Integration with Fireworks.ai API for LLM capabilities.
    
    This class provides a simplified interface for making requests to
    Fireworks.ai models, with support for various models and parameters.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        debug: bool = False
    ):
        """
        Initialize the Fireworks.ai model client.
        
        Args:
            api_key: Fireworks API key (optional, defaults to environment variable)
            model: Model identifier to use
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            presence_penalty: Penalty for token presence
            frequency_penalty: Penalty for token frequency
            debug: Enable debug logging
        """
        self.api_key = api_key or os.environ.get("FIREWORKS_API_KEY")
        if not self.api_key:
            raise ValueError("Fireworks API key is required. Provide it as a parameter or set FIREWORKS_API_KEY environment variable.")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.debug = debug
        
        # Fireworks API endpoint
        self.api_endpoint = "https://api.fireworks.ai/inference/v1/completions"
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response using the Fireworks.ai API.
        
        Args:
            system_prompt: System prompt for the model
            user_message: User message/query
            temperature: Override default temperature if provided
            max_tokens: Override default max_tokens if provided
            
        Returns:
            Generated response as a string
        """
        # Use provided parameters or defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Combine system prompt and user message into a single prompt
        combined_prompt = f"{system_prompt}\n\n{user_message}"
        
        # Prepare the API request with the prompt parameter (not messages)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "prompt": combined_prompt,
            "temperature": temp,
            "max_tokens": tokens,
            "top_p": self.top_p,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty
        }
        
        if self.debug:
            print(f"Sending request to Fireworks.ai API:\nModel: {self.model}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Send the API request with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    start_time = time.time()
                    response = await client.post(
                        self.api_endpoint,
                        headers=headers,
                        json=payload,
                        timeout=60.0  # 60 second timeout
                    )
                    
                    elapsed_time = time.time() - start_time
                    if self.debug:
                        print(f"Request completed in {elapsed_time:.2f} seconds")
                    
                    # Check for HTTP errors
                    response.raise_for_status()
                    
                    # Parse the response
                    result = response.json()
                    
                    if self.debug:
                        print(f"Received response from Fireworks.ai API")
                    
                    # Extract the generated text
                    generated_text = result.get("choices", [{}])[0].get("text", "")
                    
                    return generated_text
                    
            except httpx.HTTPStatusError as e:
                if self.debug:
                    print(f"HTTP error: {e.response.status_code} - {e.response.text}")
                
                # Handle rate limiting (status code 429)
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    if self.debug:
                        print(f"Rate limited. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # For other HTTP errors, raise the exception
                raise
                
            except (httpx.RequestError, Exception) as e:
                if self.debug:
                    print(f"Request error: {str(e)}")
                
                # Retry on connection errors
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    if self.debug:
                        print(f"Connection error. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # If all retries fail, raise the exception
                raise
        
        # If we get here, all retries failed
        raise Exception(f"Failed to get response from Fireworks.ai API after {max_retries} attempts")


class ModelFactory:
    """
    Factory class for creating model instances based on task requirements.
    
    This class provides methods to create appropriate model instances for
    different research tasks, optimizing for cost and performance.
    """
    
    @staticmethod
    def create_model(
        task_type: str,
        api_key: str,
        debug: bool = False
    ) -> FireworksModel:
        """
        Create a model instance optimized for a specific task type.
        
        Args:
            task_type: Type of task (planning, retrieval, analysis, report)
            api_key: Fireworks API key
            debug: Enable debug logging
            
        Returns:
            Configured FireworksModel instance
        """
        # Configure model parameters based on task type
        if task_type == "planning":
            # Planning needs strong reasoning for breaking down complex queries
            return FireworksModel(
                api_key=api_key,
                model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                temperature=0.2,
                max_tokens=4096,
                debug=debug
            )
        
        elif task_type == "retrieval":
            # Retrieval can use smaller models to save cost
            return FireworksModel(
                api_key=api_key,
                model="accounts/fireworks/models/llama-v3p1-8b-instruct",
                temperature=0.1,
                max_tokens=2048,
                debug=debug
            )
        
        elif task_type == "analysis":
            # Analysis needs strong reasoning for pattern recognition
            return FireworksModel(
                api_key=api_key,
                model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                temperature=0.3,
                max_tokens=4096,
                debug=debug
            )
        
        elif task_type == "report":
            # Report generation needs strong language capabilities for coherent writing
            return FireworksModel(
                api_key=api_key,
                model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                temperature=0.2,
                max_tokens=8192,
                debug=debug
            )
        
        else:
            # Default to a balanced model
            return FireworksModel(
                api_key=api_key,
                model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                temperature=0.2,
                max_tokens=4096,
                debug=debug
            )