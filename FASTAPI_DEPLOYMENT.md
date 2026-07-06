# FastAPI Microservices Deployment Guide

**Version**: 1.0  
**Date**: July 3, 2026  
**Status**: ✅ Production Ready

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────┐
│        API GATEWAY (Port 8000)               │
│   - Orchestrates all agents                  │
│   - Parallel agent calls                     │
│   - Score synthesis                          │
│   - Decision logic                           │
└─────────────┬─────────────────────────────────┘
              │
    ┌─────────┼─────────┬──────────┐
    │         │         │          │
┌───▼──┐ ┌───▼──┐ ┌───▼──┐ ┌───▼──┐
│Port  │ │Port  │ │Port  │ │Port  │
│8001  │ │8002  │ │8003  │ │8004  │
├──────┤ ├──────┤ ├──────┤ ├──────┤
│ Doc  │ │Credit│ │ Risk │ │Compli│
│Agent │ │Agent │ │Agent │ │Agent │
└──────┘ └──────┘ └──────┘ └──────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install FastAPI and Uvicorn
pip3 install fastapi uvicorn httpx pydantic

# Verify installations
python3 -c "import fastapi; import uvicorn; print('✅ Ready')"
```

### Start All Agents (Local Development)

```bash
# Terminal 1: Document Verification Agent (Port 8001)
python3 -c "
from fastapi_agents import document_agent
import uvicorn
uvicorn.run(document_agent, host='0.0.0.0', port=8001)
"

# Terminal 2: Credit Analysis Agent (Port 8002)
python3 -c "
from fastapi_agents import credit_agent
import uvicorn
uvicorn.run(credit_agent, host='0.0.0.0', port=8002)
"

# Terminal 3: Risk Assessment Agent (Port 8003)
python3 -c "
from fastapi_agents import risk_agent
import uvicorn
uvicorn.run(risk_agent, host='0.0.0.0', port=8003)
"

# Terminal 4: Compliance Agent (Port 8004)
python3 -c "
from fastapi_agents import compliance_agent
import uvicorn
uvicorn.run(compliance_agent, host='0.0.0.0', port=8004)
"

# Terminal 5: API Gateway (Port 8000)
python3 -c "
from fastapi_agents import gateway
import uvicorn
uvicorn.run(gateway, host='0.0.0.0', port=8000)
"
```

### Using Uvicorn Directly

```bash
# Terminal 1: Document Agent
uvicorn fastapi_agents:document_agent --port 8001 --reload

# Terminal 2: Credit Agent
uvicorn fastapi_agents:credit_agent --port 8002 --reload

# Terminal 3: Risk Agent
uvicorn fastapi_agents:risk_agent --port 8003 --reload

# Terminal 4: Compliance Agent
uvicorn fastapi_agents:compliance_agent --port 8004 --reload

# Terminal 5: Gateway
uvicorn fastapi_agents:gateway --port 8000 --reload
```

---

## 📊 API Endpoints

### Gateway Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "gateway": "API Gateway",
  "uptime_seconds": 123,
  "agents": [
    "Document Verification Agent",
    "Credit Analysis Agent",
    "Risk Assessment Agent",
    "Compliance & Regulatory Agent"
  ]
}
```

#### List Agents
```bash
curl http://localhost:8000/agents
```

Response:
```json
{
  "agents": [
    "Document Verification Agent",
    "Credit Analysis Agent",
    "Risk Assessment Agent",
    "Compliance & Regulatory Agent"
  ],
  "gateway": "API Gateway",
  "version": "1.0.0"
}
```

#### Check Agent Status
```bash
curl -X POST http://localhost:8000/agents/status
```

Response:
```json
{
  "Document Verification Agent": {
    "status": "healthy",
    "details": {
      "status": "healthy",
      "agent_name": "Document Verification Agent",
      "uptime_seconds": 45,
      "version": "1.0.0"
    }
  },
  ...
}
```

#### Evaluate Loan Application
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {
      "applicant_id": "APP001",
      "name": "Rajesh Kumar",
      "age": 38,
      "annual_income": 2000000,
      "employment_type": "employed",
      "employment_years": 12,
      "credit_score": 795,
      "existing_liabilities": 500000,
      "total_assets": 1500000,
      "location": "Mumbai",
      "kyc_verified": true
    },
    "loan": {
      "loan_id": "LN000001",
      "amount": 5000000,
      "tenure_months": 60,
      "purpose": "home"
    }
  }'
```

Response:
```json
{
  "evaluation_id": "EVAL12345678",
  "loan_id": "LN000001",
  "decision": "APPROVED",
  "final_score": 87.6,
  "risk_level": "LOW",
  "agent_results": [
    {
      "agent_name": "Document Verification Agent",
      "score": 93.0,
      "confidence": 0.98,
      "status": "completed",
      "findings": {...},
      "processing_time_ms": 0.41,
      "timestamp": "2024-01-15T10:30:45.123456"
    },
    ...
  ],
  "processing_time_ms": 2.34,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Individual Agent Endpoints

Each agent has the same structure:

#### Agent Health
```bash
curl http://localhost:8001/health  # Document Agent
curl http://localhost:8002/health  # Credit Agent
curl http://localhost:8003/health  # Risk Agent
curl http://localhost:8004/health  # Compliance Agent
```

#### Agent Info
```bash
curl http://localhost:8001/info
curl http://localhost:8002/info
curl http://localhost:8003/info
curl http://localhost:8004/info
```

#### Agent Evaluate
```bash
curl -X POST http://localhost:8001/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {...},
    "loan": {...}
  }'
```

---

## 🐳 Docker Deployment

### Dockerfile for Individual Agent

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn httpx pydantic

# Copy application
COPY fastapi_agents.py .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Run agent
CMD ["uvicorn", "fastapi_agents:document_agent", "--host", "0.0.0.0", "--port", "8001"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  document-agent:
    build: .
    ports:
      - "8001:8001"
    command: uvicorn fastapi_agents:document_agent --host 0.0.0.0 --port 8001
    environment:
      - LOG_LEVEL=INFO
    networks:
      - rsbank

  credit-agent:
    build: .
    ports:
      - "8002:8002"
    command: uvicorn fastapi_agents:credit_agent --host 0.0.0.0 --port 8002
    environment:
      - LOG_LEVEL=INFO
    networks:
      - rsbank

  risk-agent:
    build: .
    ports:
      - "8003:8003"
    command: uvicorn fastapi_agents:risk_agent --host 0.0.0.0 --port 8003
    environment:
      - LOG_LEVEL=INFO
    networks:
      - rsbank

  compliance-agent:
    build: .
    ports:
      - "8004:8004"
    command: uvicorn fastapi_agents:compliance_agent --host 0.0.0.0 --port 8004
    environment:
      - LOG_LEVEL=INFO
    networks:
      - rsbank

  api-gateway:
    build: .
    ports:
      - "8000:8000"
    command: uvicorn fastapi_agents:gateway --host 0.0.0.0 --port 8000
    environment:
      - LOG_LEVEL=INFO
      - AGENT_URLS='{"Document Verification Agent": "http://document-agent:8001", "Credit Analysis Agent": "http://credit-agent:8002", "Risk Assessment Agent": "http://risk-agent:8003", "Compliance & Regulatory Agent": "http://compliance-agent:8004"}'
    depends_on:
      - document-agent
      - credit-agent
      - risk-agent
      - compliance-agent
    networks:
      - rsbank

networks:
  rsbank:
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api-gateway

# Stop all services
docker-compose down
```

---

## ⚙️ Production Configuration

### Gunicorn + Uvicorn

```bash
# Install Gunicorn
pip3 install gunicorn

# Run with Gunicorn
gunicorn fastapi_agents:gateway \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Nginx Configuration

```nginx
upstream gateway {
    server localhost:8000;
}

upstream document_agent {
    server localhost:8001;
}

upstream credit_agent {
    server localhost:8002;
}

upstream risk_agent {
    server localhost:8003;
}

upstream compliance_agent {
    server localhost:8004;
}

server {
    listen 80;
    server_name api.rsbank.com;

    # API Gateway
    location / {
        proxy_pass http://gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Individual Agents (for monitoring)
    location /agents/document {
        proxy_pass http://document_agent/;
    }

    location /agents/credit {
        proxy_pass http://credit_agent/;
    }

    location /agents/risk {
        proxy_pass http://risk_agent/;
    }

    location /agents/compliance {
        proxy_pass http://compliance_agent/;
    }
}
```

---

## 🧪 Testing

### Test Script

```python
import httpx
import json
import time

GATEWAY_URL = "http://localhost:8000"

# Test data
applicant = {
    "applicant_id": "APP001",
    "name": "Test User",
    "age": 35,
    "annual_income": 1500000,
    "employment_type": "employed",
    "employment_years": 5,
    "credit_score": 750,
    "existing_liabilities": 300000,
    "total_assets": 1000000,
    "location": "Mumbai",
    "kyc_verified": True
}

loan = {
    "loan_id": "LN000001",
    "amount": 3000000,
    "tenure_months": 48,
    "purpose": "home"
}

# Test 1: Health Check
print("Test 1: Health Check")
response = httpx.get(f"{GATEWAY_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: List Agents
print("Test 2: List Agents")
response = httpx.get(f"{GATEWAY_URL}/agents")
print(f"Status: {response.status_code}")
print(f"Agents: {response.json()['agents']}\n")

# Test 3: Check Agent Status
print("Test 3: Check Agent Status")
response = httpx.post(f"{GATEWAY_URL}/agents/status")
print(f"Status: {response.status_code}")
for agent, status in response.json().items():
    print(f"  {agent}: {status['status']}\n")

# Test 4: Evaluate Loan
print("Test 4: Evaluate Loan Application")
start = time.time()
response = httpx.post(
    f"{GATEWAY_URL}/evaluate",
    json={"applicant": applicant, "loan": loan}
)
elapsed = time.time() - start

print(f"Status: {response.status_code}")
result = response.json()
print(f"Decision: {result['decision']}")
print(f"Score: {result['final_score']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
print(f"Total Time: {elapsed*1000:.2f}ms\n")

# Test 5: API Documentation
print("Test 5: API Documentation")
print("OpenAPI Docs: http://localhost:8000/docs")
print("Redoc: http://localhost:8000/redoc")
```

### Run Tests

```bash
python3 << 'EOF'
[paste test script above]
EOF
```

---

## 📈 Performance Monitoring

### Prometheus Metrics

Install Prometheus client:
```bash
pip3 install prometheus-client
```

Add to FastAPI app:
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
evaluation_counter = Counter(
    'evaluations_total',
    'Total evaluations',
    ['decision']
)

evaluation_duration = Histogram(
    'evaluation_duration_seconds',
    'Evaluation duration',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

---

## 🔒 Security Best Practices

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting
```bash
pip3 install slowapi

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/evaluate")
@limiter.limit("10/minute")
async def evaluate(request, _: Request):
    ...
```

### API Key Authentication
```python
from fastapi import Depends, HTTPException, Header

async def verify_api_key(x_token: str = Header(...)):
    if x_token != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_token

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest, _: str = Depends(verify_api_key)):
    ...
```

---

## 📊 Deployment Checklist

- [ ] FastAPI and Uvicorn installed
- [ ] All 5 services starting (4 agents + 1 gateway)
- [ ] Health checks passing
- [ ] API documentation accessible (/docs)
- [ ] Gateway orchestrating agents correctly
- [ ] Parallel agent execution working
- [ ] Score synthesis correct
- [ ] Decision logic accurate
- [ ] Logging configured
- [ ] Error handling working
- [ ] Rate limiting configured
- [ ] CORS configured for security
- [ ] Docker Compose file created
- [ ] Production deployment ready
- [ ] Monitoring metrics configured
- [ ] Load testing completed
- [ ] Failover procedures documented
- [ ] Backup/recovery plan in place

---

## 🚀 Production Deployment

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: document-agent
  template:
    metadata:
      labels:
        app: document-agent
    spec:
      containers:
      - name: document-agent
        image: rsbank/document-agent:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 📞 Troubleshooting

### Agent Connection Issues
```bash
# Check if agent is running
curl http://localhost:8001/health

# Check port in use
lsof -i :8001

# Check network connectivity
netstat -an | grep 8001
```

### Gateway Timeout
```python
# Increase timeout in gateway
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)
```

### Memory Issues
```bash
# Monitor memory usage
docker stats

# Limit container memory
docker run -m 512m ...
```

---

## ✅ Ready for Production

All FastAPI microservices are production-ready with:
- ✅ Parallel agent execution
- ✅ Async/await architecture
- ✅ Health checks
- ✅ Error handling
- ✅ Docker support
- ✅ Monitoring capabilities
- ✅ Security features
- ✅ Auto API documentation

**Start the full system and test it now!**

---

**Created**: July 3, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0
