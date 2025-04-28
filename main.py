import os
import argparse
from sentient_agent_framework import DefaultServer
from research_agent.agent import DeepResearchAgent

def main():
    """
    Main entry point for running the Deep Research Agent with the Sentient Agent Framework.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Deep Research Agent for Sentient Chat")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--fireworks-api-key", type=str, help="Fireworks API key (optional, can also use FIREWORKS_API_KEY env var)")
    parser.add_argument("--jina-api-key", type=str, help="Jina API key (optional, can also use JINA_API_KEY env var)")
    args = parser.parse_args()
    
    # Get API keys from arguments or environment variables
    fireworks_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    jina_api_key = args.jina_api_key or os.environ.get("JINA_API_KEY")
    
    # Check for required API keys
    if not fireworks_api_key:
        raise ValueError("Fireworks API key is required. Provide it as a command line argument or set FIREWORKS_API_KEY environment variable.")
    
    # Create the Deep Research Agent
    print("Initializing Deep Research Agent...")
    agent = DeepResearchAgent(
        name="Deep Research Agent",
        fireworks_api_key=fireworks_api_key,
        jina_api_key=jina_api_key,
        debug=args.debug
    )
    
    # Create and run the server
    print(f"Starting server on {args.host}:{args.port}...")
    server = DefaultServer(agent)
    server.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
