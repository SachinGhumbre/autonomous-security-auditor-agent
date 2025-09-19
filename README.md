#### Autonomous Security Auditor Agents (backend) - Installation Steps ###
--------------------------------------------------------------------------

### Agentic AI Application with Kong API Gateway + Flask + LangGraph + Python

## Setup Agentic AI Backend Application
- Setup Agentic AI backend application using Flask + LangGraph + Python

# Install python libraries on local system
- put all library names in requirements.txt file, one at one line
- run commands
cd autonomous-security-auditor-agent
pip install -r requirements.txt

# Run on local or server
- create virtual environment
python -m venv venv
venv\Scripts\activate
- run the application
python init_auditor.py
- invoke Generate audit report API and then Remediation API
- Test Audit and Remediate APIs (Flask)
http://{HOSTNAME}:5000/audit
http://{HOSTNAME}:5000/remediate

## Setup Kong API Proxies
- create proxy for Agentic AI - Flask APIs /audit and /remediate
<<add steps here>> or kong config file
- we have deployed agents APIs on the same EC2 server where Kong DP is deployed. this is just for demo purpose.
- Test Agentic APIs through Kong gateway


##### RAG Pipeline (backend) using Kong AI Gateway
--------------------------------------------------

# Install Redis Vector Database
- run below command on the same EC2 instance. this is just for demo purpose.
docker compose up -d
OR
helm repo add redis-stack https://redis-stack.github.io/helm-redis-stack
help repo update
helm install redis-stack redis-stack/redis-stack -n redis --create-namespace


# Ingest Knowledge Base to Vector Database
- Ingest knowledge base to the vector DB. 
- Knowledge base is in /backend/knowledge_base
- run command
cd backend/rag
python knowledge_ingestor.py

# Create AI Gateway 
- create AI gateway using Konnect
<<Add steps here>> or kong.yaml file

- Add AI RAG Injector Plugin to AI gateway service
redist_host:redis
template:<CONTEXT> | <PROMPT>
role: user
Distance metrics: Consine
dimensions: 1536
-<<UPDATE ME>> add complete AI RAG Injector plugin code here, added on LLM service


##### UI for Agentic AI Application (frontend) using React.js + Tailwindcss + Typescript
---------------------------------------------------------------------------------------
- UI for Agentic AI Application connects Agentic AI backend through Kong API Gateway
- deploy it in AWS S3 bucket. this is just for demo purpose
- ensure frontend is connecting to Kong APIs
- run commands
cd autonomous-security-auditor-agent/frontend
npm install
npm run build
- Upload the contents of the `build` folder to your S3 bucket.

- Enable static website hosting in the S3 bucket settings.

-  Set the index document to `index.html` and error document to `index.html`.

-  Make the bucket public or use CloudFront for secure access.


##### Key Notes 
----------------
1. We assumed you already have setup Kong Konnect and Dataplane node setup
2. You know python
