from setuptools import setup, find_packages

setup(
    name="research_agent",
    version="0.1.0",
    description="Deep Research Agent for Sentient Chat",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "sentient-agent-framework>=0.1.0",
        "httpx>=0.24.1",
        "jina>=2.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
)
