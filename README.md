# Deep Research Agent for Sentient Chat

A sophisticated multi-agent research system that delivers comprehensive, well-structured research reports on complex topics. This agent orchestrates specialized sub-agents to break down research tasks, gather information, analyze content, and synthesize findings into detailed reports.

## Features

- **Multi-agent Architecture**: Coordinated system of specialized agents working together
- **Comprehensive Research Planning**: Breaks down queries into specific research tasks
- **Deep Information Retrieval**: Simulates advanced information retrieval with reranking
- **Insightful Content Analysis**: Extracts key insights and patterns from retrieved information
- **Professional Report Generation**: Synthesizes findings into well-structured research reports
- **Persistent Memory**: Maintains research context across interactions
- **Streaming Progress Updates**: Provides real-time updates throughout the research process

## Requirements

- Python 3.8+
- Fireworks.ai API key
- Jina AI API key (optional, for semantic reranking)

## Installation

### Option 1: Install from source

```bash
git clone https://github.com/yourusername/research-agent.git
cd research-agent
pip install -e .
```

### Option 2: Install using pip

```bash
pip install git+https://github.com/yourusername/research-agent.git
```

## AWS EC2 Deployment

To deploy the Research Agent on AWS EC2:

1. **Launch an EC2 instance**:
   - Recommended: t3.medium or larger
   - Ubuntu Server 20.04 LTS
   - At least 20GB storage

2. **Connect to your instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-public-dns
   ```

3. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git
   ```

4. **Clone and install the agent**:
   ```bash
   git clone https://github.com/yourusername/research-agent.git
   cd research-agent
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

5. **Set up environment variables**:
   ```bash
   echo 'export FIREWORKS_API_KEY="your-fireworks-api-key"' >> ~/.bashrc
   echo 'export JINA_API_KEY="your-jina-api-key"' >> ~/.bashrc
   source ~/.bashrc
   ```

6. **Run the agent with screen** (keeps it running after you disconnect):
   ```bash
   screen -S research-agent
   cd ~/research-agent
   source venv/bin/activate
   python main.py --port 8000
   ```
   
   Press `Ctrl+A` then `D` to detach from the screen.
   
   To reattach later:
   ```bash
   screen -r research-agent
   ```

7. **Set up a systemd service** (alternative to screen):
   ```bash
   sudo nano /etc/systemd/system/research-agent.service
   ```
   
   Add the following content:
   ```
   [Unit]
   Description=Research Agent for Sentient Chat
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/research-agent
   ExecStart=/home/ubuntu/research-agent/venv/bin/python main.py --port 8000
   Restart=always
   Environment="FIREWORKS_API_KEY=your-fireworks-api-key"
   Environment="JINA_API_KEY=your-jina-api-key"

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start the service:
   ```bash
   sudo systemctl enable research-agent
   sudo systemctl start research-agent
   ```
   
   Check status:
   ```bash
   sudo systemctl status research-agent
   ```

8. **Set up NGINX as a reverse proxy** (optional):
   ```bash
   sudo apt install -y nginx
   sudo nano /etc/nginx/sites-available/research-agent
   ```
   
   Add the following content:
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```
   
   Enable the site and restart NGINX:
   ```bash
   sudo ln -s /etc/nginx/sites-available/research-agent /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Set up SSL with Certbot** (optional):
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Usage

### Running the agent directly

```bash
# Set your API keys
export FIREWORKS_API_KEY="your-fireworks-api-key"
export JINA_API_KEY="your-jina-api-key"  # Optional

# Run the agent
python main.py --port 8000
```

### Using the agent in Sentient Chat

Once deployed, the agent can be accessed through the Sentient Chat interface by configuring the agent endpoint URL.

## Configuration Options

The agent accepts the following command-line arguments:

- `--host`: Host to bind the server to (default: `0.0.0.0`)
- `--port`: Port to bind the server to (default: `8000`)
- `--debug`: Enable debug mode (default: `False`)
- `--fireworks-api-key`: Fireworks API key (alternative to using environment variable)
- `--jina-api-key`: Jina API key (alternative to using environment variable)

## Architecture

The Research Agent is built using a multi-agent architecture with specialized components:

1. **Research Coordinator**: Manages the overall research process
2. **Research Planner**: Analyzes queries and creates research plans
3. **Information Retriever**: Gathers information from various sources
4. **Content Analyzer**: Evaluates and extracts insights from information
5. **Report Generator**: Synthesizes findings into comprehensive reports
6. **Research Memory**: Maintains state and tracks research progress

## License

This project is licensed under the MIT License - see the LICENSE file for details.
