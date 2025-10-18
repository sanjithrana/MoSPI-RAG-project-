# MoSPI-RAG-project-

# 📊 MoSPI RAG Data Pipeline and Chatbot

**Author:** SANJITH CHILUPURI 
**Project:** Data AI & ML Internship Assignment  
**Date:** October 2025  

---

## 🧠 Overview

This project is an end-to-end **Retrieval-Augmented Generation (RAG)** system built around the **Ministry of Statistics and Programme Implementation (MoSPI)** data.  
It scrapes official documents, processes and embeds their contents, and allows users to query them via a chatbot-style interface.

The system integrates:
- **Data Scraping**
- **ETL (Extract, Transform, Load) pipeline**
- **Vector-based retrieval**
- **FastAPI backend**
- **Streamlit UI frontend**
- **Dockerized deployment**

---

## 🏗️ System Architecture

```text
        +-------------------+
        |  MoSPI Website    |
        +---------+---------+
                  |
                  v
        +-------------------+
        |  Scraper (crawl.py)|
        +---------+---------+
                  |
                  v
        +-------------------+
        |  ETL Pipeline     |
        |  - Extract PDFs   |
        |  - Clean & Chunk  |
        |  - Generate Embeddings |
        +---------+---------+
                  |
                  v
        +-------------------+
        |  FAISS Index + DB |
        +---------+---------+
                  |
                  v
        +-------------------+
        |  FastAPI Backend  |
        +---------+---------+
                  |
                  v
        +-------------------+
        |  Streamlit UI     |
        +-------------------+
📁 Folder Structure
markdown
Copy code
Data_AI_ML_Assignment/
│
├── scraper/
│   ├── crawl.py
│   ├── parse.py
│   ├── models.py
│   └── __init__.py
│
├── pipeline/
│   ├── run.py
│   ├── validate.py
│   └── __init__.py
│
├── rag/
│   ├── api.py
│   ├── retriever.py
│   ├── prompt.py
│   └── __init__.py
│
├── ui/
│   └── streamlit_app.py
│
├── infra/
│   ├── Dockerfile.api
│   └── Dockerfile.ui
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── Makefile
└── README.md
⚙️ Installation & Setup
🔹 1. Local Setup (without Docker)
Step 1: Clone or unzip the project

bash
Copy code
git clone https://github.com/yourusername/mospi-rag-project.git
cd mospi-rag-project
Step 2: Create and activate virtual environment

bash
Copy code
python -m venv hello_env
.\hello_env\Scripts\activate
Step 3: Install dependencies

bash
Copy code
pip install -r requirements.txt
Step 4: Run the FastAPI backend

bash
Copy code
python -m rag.api
Open http://localhost:8000/health to verify it’s running.

Step 5: In another terminal, start Streamlit UI

bash
Copy code
streamlit run ui/streamlit_app.py
Now open http://localhost:8501 to use the chatbot interface.

🔹 2. Run with Docker
Make sure Docker Desktop is running, then execute:

bash
Copy code
docker compose up --build
This will build and start both services:

FastAPI API → http://localhost:8000

Streamlit UI → http://localhost:8501

🧱 Docker Configuration
infra/Dockerfile.api
Builds the backend service:

dockerfile
Copy code
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "-m", "rag.api"]
infra/Dockerfile.ui
Builds the Streamlit UI service:

dockerfile
Copy code
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
docker-compose.yml
Defines both services:

yaml
Copy code
services:
  api:
    build:
      context: .
      dockerfile: infra/Dockerfile.api
    ports:
      - "8000:8000"

  ui:
    build:
      context: .
      dockerfile: infra/Dockerfile.ui
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
✅ What Worked
Web scraping and data ingestion from MoSPI website

PDF text extraction and metadata parsing

Embedding generation using sentence-transformers

FAISS-based semantic retrieval

FastAPI endpoints: /ask, /health, /ingest

Streamlit user interface

Full Dockerized environment (API + UI)

⚠️ What Didn’t Work / Challenges
Some PDFs (scanned images) couldn’t be parsed properly

Docker builds were slow due to large dependencies (torch, faiss)

OneDrive syncing caused path issues — solved by moving project to a local drive

LLM integration for text generation still pending

🚀 Next Steps
Integrate LLaMA 3 / Ollama for generative answers

Add automatic daily MoSPI data updates

Use ChromaDB or pgvector for scalable vector storage

Deploy to AWS ECS / Render / Railway

Improve UI with contextual highlighting and citations

📧 Author
sanjith chilupuri
chilupurisanjith18@gmail.com
October 2025

This project was completed as part of the Data AI & ML Internship Assignment, demonstrating full-stack AI data engineering, retrieval, and web application deployment.





