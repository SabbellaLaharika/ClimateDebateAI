# AI-Powered Climate Policy Debate Simulator

A multi-agent AI application that simulates a structured debate on climate policy between the USA, EU, and China. 
It uses **FastAPI**, **Ollama** (for local LLMs), and a **ChromaDB**-powered Retrieval-Augmented Generation (RAG) system to ground each agent's arguments in their actual policy documents.

## Features
- **Multi-Agent Simulation**: Three distinct agents (USA, EU, China) debate in a fixed, turn-based order.
- **Local-First RAG**: Uses ChromaDB and sentence-transformers to retrieve relevant policy points entirely locally.
- **State Management**: Maintains debate history and conversational state across rounds.
- **REST API**: Built with FastAPI for high performance and automatic documentation.
- **Modern UI**: A responsive, premium web interface for visualizing the debate as it happens.

## Requirements
- Docker and Docker Compose

## Setup and Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SabbellaLaharika/ClimateDebateAI.git
   cd ClimateDebateAI
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env`. The defaults are fine for local use.
   ```bash
   cp .env.example .env
   ```

3. **Run the Application:**
   Start the services using Docker Compose. The API will wait for Ollama to become healthy.
   ```bash
   docker-compose up -d --build
   ```

4. **Pull the LLM Model:**
   You must pull the `llama3:8b` model inside the running Ollama container:
   ```bash
   docker-compose exec ollama ollama pull llama3:8b
   ```

5. **Access the Application:**
   - **Frontend UI**: [http://localhost:8000/](http://localhost:8000/)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

## Architecture Overview
- **`main.py`**: FastAPI entry point, handles endpoints and orchestrates the turn-based loop.
- **`agents/debater.py`**: Interacts with the local LLM and formats the system prompt with context and history.
- **`core/rag_service.py`**: Initializes ChromaDB, ingests JSON policies, and retrieves relevant context.
- **`data/policies/`**: The knowledge base of JSON documents.
