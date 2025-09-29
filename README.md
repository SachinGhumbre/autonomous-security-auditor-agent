# 🚀 Project Title: Autonomous Security Auditor Agentic AI

## 🧠 Project Description

**Autonomous Security Auditor Agentic AI** is a cutting-edge solution that transforms how enterprises audit and secure their APIs on **Kong API Gateway** and **Kong AI Gateway**. By combining **Agentic AI workflows**, **LLMs**, and **Kong’s intelligent plugins**, this tool autonomously audits API configurations against enterprise security policies and enables one-click remediation—empowering teams to maintain compliance effortlessly.

## 🔍 What Problem Does It Solve?

In large organizations, enforcing consistent API security policies—like authentication, authorization, GDPR compliance, and naming standards—is a daunting challenge. Manual reviews are slow, error-prone, and require deep policy expertise. This leads to:

- Security gaps and data exposure  
- Non-compliance with internal and external regulations  
- Increased operational overhead for DevSecOps teams  

## 🛠️ How Does It Solve It?

Our agentic solution **automates the entire audit lifecycle**:

- **Continuously scans Kong API configurations**  
- **Validates them against enterprise security policies**  
- **Generates actionable audit reports**  
- **Offers one-click remediation**  

It empowers developers, architects, and auditors to ensure every API is secure and compliant—without needing to be policy experts.

## 🤖 How It Relates to the Agentic AI Theme

This project is a **true embodiment of Agentic AI**:

- **Autonomous agents** perform audits and remediation  
- **LLMs** interpret complex policy documents and apply them contextually  
- **Kong AI Gateway** powers intelligent prompt injection, retrieval-augmented generation (RAG), and ethical filtering  
- **LangGraph orchestration** enables multi-agent collaboration for scalable, intelligent decision-making  

## 🧩 Why Kong AI Gateway Is Critical

Kong AI Gateway is the **intelligence engine** behind this solution. With features like:

- **AI Proxy** for seamless LLM integration  
- **RAG Injector** for real-time policy retrieval  
- **Prompt Guard** for ethical and secure prompt handling  
- **Response Transformer** for dynamic output shaping  

…it ensures every audit is **context-aware, policy-driven, and performance-optimized**. Without Kong AI Gateway, this level of autonomy and precision wouldn’t be possible.


# Solution Architecture
![alt text](<High level design .png>)

![alt text](<Complete Architecture of Autonomous Security Auditor.png>)

## Agentic AI Tools Developed
As part of this Agentic AI application, two major AI agents were developed:
- Agentic AI Application (React UI + Kong API and AI Agents + LangGraph + Flask + Azure LLM)
- RAG Pipeline (Kong AI Gateway + Redis as VectorDB + Azure LLM)

## Technology Stack
- Kong AI Gateway
- Kong API Gateway
- Redis as VectorDB
- Python + Flask + LangGraph
- ReactJS + TailwindCss + Typescript
- AI Technologies - Any LLM e.g. Azure gpt-4.1 model, OpenAI Embedding Model


## Kong AI Plugins Used

| Kong AI Feature/Plugin | Strategic Value for Autonomous Security Auditor Agent |
|------------------------|--------------------------------------------------------|
| AI Proxy Advanced | Enabled seamless integration of multiple LLMs (Azure GPT-4.1, Gemini-2-Flash) through a unified API layer. This allowed the agent to intelligently route requests based on audit context, improving performance and scalability across diverse security validation tasks. |
| AI Rate Limiting Advanced | Enforced granular usage controls per consumer application, ensuring cost-effective LLM consumption. This was critical for managing token budgets while maintaining high availability of the auditing agent across teams. |
| AI Prompt Decorator | Injected system-level context into every prompt, ensuring the LLM consistently operated as a focused security auditor. This improved audit precision and reduced prompt engineering overhead. |
| AI Prompt Guard | Applied ethical and hallucination filters to LLM inputs, safeguarding the agent from generating misleading or non-compliant audit results. This enhanced trust and reliability in automated policy enforcement. |
| AI RAG Injector | Built a dynamic RAG pipeline that injected enterprise security policies as context during audits. This eliminated the need for extensive LLM fine-tuning, reduced operational costs, and ensured real-time policy-aware compliance checks. |
| AI Response Transformer | Transformed verbose LLM outputs into structured audit reports containing only relevant fields (e.g., service name, compliance status, violated policies). This streamlined reporting and improved clarity for DevSecOps teams. |
| Unified LLM Dashboard | Provided a centralized view of agent activity, token usage, and consumer behavior. This enabled governance, cost tracking, and performance optimization of the Autonomous Security Auditor Agent across the organization. |


## API Catalog

| API Name                        | Description                                                        | API URL                                                                 | Method |
|----------------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------|--------|
| Ingest Knowledge API (Kong API GW)      | Ingest organization security policies to the Redis vector database         | http://localhost:5001/api/v1/knowledge/ingest OR https://{KONG_DP_DNS}/api/v1/knowledge/ingest                           | POST   |
| Auditor Agent AI API (Kong AI GW)       | Azure LLM exposed via Kong AI gateway's unified API                       | https://{KONG_DP_DNS}/api/v1/agents/auditor             | POST   |
| Audit API Configs API (Kong API GW)     | Audit AI Agent API used to audit Kong configurations                       | http://localhost:5000/api/v1/ai-agents/audit OR https://{KONG_DP_DNS}/api/v1/ai-agents/audit                            | POST   |
| Remediate API Configs API (Kong API GW) | Enables remediation as per organization security policies                  | http://localhost:5000/api/v1/ai-agents/remediate OR https://{KONG_DP_DNS}/api/v1/ai-agents/remediate                        | POST   |


# Installation and Setup Prerequisites

## Frontend Requirements

Install the following technologies on the system where the UI application will run:
- ReactJS
- TailwindCSS
- npm
- TypeScript

## Backend Requirements

- Access to Kong products:
  - Kong Konnect
  - Kong Gateway
  - Kong AI Gateway
- Python and required libraries listed in `requirements.txt`
- Environment variables configured in the `.env` file
- Organization-specific security policies placed in the `knowledge_base` directory
- Redis database installed and accessible from Kong Gateway server
- Docker installed (if using containerized setup)
- Credentials and configuration details for LLM models (e.g., Azure GPT-4.1, text-embedding-3-small)


# 🛠️ Installation Guide

This project implements a complete **RAG-based Agentic AI pipeline** using Kong AI Gateway, Azure GPT-4.1, OpenAI Embedding, Redis VectorDB, LangGraph, Flask, and React. It includes:

- **RAG Pipeline (Backend)** for ingesting and querying security policies.
- **Agentic AI (Backend)** with Audit and Remediation agents.
- **ReactJS UI (Frontend)** for interacting with the system.

---

## 📦 RAG Pipeline Setup (Backend)

### 1. Install Redis Vector Database

Redis is used as the VectorDB for storing embedded security policies.

**For development environment:**


#### Option 1: Docker
```
docker compose up -d
```

#### Option 2: Helm
```
helm repo add redis-stack https://redis-stack.github.io/helm-redis-stack
helm repo update
helm install redis-stack redis-stack/redis-stack -n redis --create-namespace
```

### Create Organization Security Policies
- Create organization specific mandatory security policies and store them in knowledge_base directory
- I created few sample files, you can refer those
- We will ingest these security policies into organization knowledge base vector database later

### Run Ingest Knowledge Python
```
cd rag
python knowledge_ingestor.py
```
### Kong AI Gateway Configuration
- ensure to create Kong AI gateway, service, routes, attach various AI plugins
- kong.yaml contains all kong AI configuration details, just publish them to Kong gateway
- ensure to have consumer app key with you

## Installatin Steps - Agentic AI (backend) - Audit and Remediation Agents

we developed two agents audit and remediation. Audit agent will fetch kong configurations from kong gateway using kong adming apis and send plugin configuration to LLM and RAG API to validate comply status 

Remediation agent will prepare remediation plan based on audit report
We are using Python, LangGraph, React, Flask to create AI agents, Kong API gateway to create API for agents

### Install python libraries system
- put all library names in requirements.txt file, one at one line
- run commands
```
cd autonomous-security-auditor-agent
pip install -r requirements.txt
```

### Run AI Agents - Audit and Remediate
- create virtual environment
```
python -m venv venv
venv\Scripts\activate
python init_auditor.py
```
- Refer API catalog for APIs

### Develop Kong API Proxies
- create proxy for Agentic AI - Flask APIs /audit and /remediate
- These are traditional Kong API proxies where we can add security
- I have used Flask API routes on my local system, hence not sharing Kong API proxies for audit and remediate APIS


### Install ReactJS UI for Agentic AI Application (frontend)
- UI for Agentic AI Application connects Agentic AI backend through Kong API Gateway
- using React.js + Tailwindcss + Typescript
- ensure frontend is connecting to Kong APIs
- run commands
```
cd autonomous-security-auditor-agent/frontend
npm install
npm start
```

# Testing Process
1. Run Knowledge Ingestion Python server (if not ran already)
```
cd autonomous-security-auditor-agent/backend/rag
python knowledge_ingestor.py
```
2. Configure Knowledge Ingestion API in Dashboard.jsx
    http://localhost:5001/api/v1/knowledge/ingest

3. Run Audit and Remediate Agents
```   
cd autonomous-security-auditor-agent/backend/agents
python init_auditor.py
```
4. Configure Audit and Remediate Agents APIs in Dashboard
    http://localhost:5000/api/v1/ai-agents/audit
    http://localhost:5000/api/v1/ai-agents/remediate


5. Start UI Application
```
cd autonomous-security-auditor-agent/frontend/
npm start
```

6. Open UI Application

- Open http://localhost:3000/
```
username: kong_champion, password: Kong@123
```
- Click on `Ingest Security Policies` to ingest security policies to Redis database
- Click on `Start Security Audit and Generate Report` to start validating your Kong proxies/services whether follow organizaton security polices and do not miss any mandatory plugins
- Click on `Run Remediation Plan`

# User Manual - Steps to Execute the Application
- Refer below document for detailed steps to execute the Autonomous Security Auditor Agentic AI application.

[User Manual - Execution Steps for Autonomous Security Auditor Agents.pdf](<User Manual - Execution Steps for Autonomous Security Auditor Agents.pdf>)

