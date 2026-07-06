# RS Bank Loan Approval - Quick Reference Guide
## Senior Developer Cheat Sheet

---

## 📋 1. System Overview (30 seconds)

**What**: Multi-Agent Agentic AI system evaluating loan applications  
**Why**: Automate decisions, improve consistency, scale to 10K+/month  
**How**: 4 specialized agents → parallel evaluation → composite score → decision  
**SLA**: <100ms per application, 80+ apps/sec throughput

---

## 🏗️ 2. Architecture Layers

```
UI (Streamlit)
    ↓
API (FastAPI) - Rate limit, validate
    ↓
Orchestrator (LangGraph) - Coordinate agents
    ↓
Agents (4 parallel):
  • Document (15%)
  • Credit (30%)
  • Risk (30%)
  • Compliance (25%)
    ↓
MCP Servers - Data access, notifications
    ↓
Decision Output → Notifications → Audit Log
```

---

## 🤖 3. Agent Weights & Scoring

| Agent | Weight | Key Metrics |
|-------|--------|-------------|
| Document | 15% | Completeness, consistency, anomalies |
| Credit | 30% | Score, history, defaults, bankruptcy |
| Risk | 30% | DTI, LTV, employment, income adequacy |
| Compliance | 25% | Age, KYC, AML, loan limits |

**Final Score** = Σ(Agent_Score × Weight)

---

## ✅ 4. Decision Thresholds

| Score | Decision | Action |
|-------|----------|--------|
| ≥70 + no flags | ✅ APPROVED | Send approval letter |
| 45-70 + flags | ⚠️ REVIEW | Route to senior officer |
| <45 or critical | ❌ REJECTED | Send rejection notice |

**Critical Flags**: UNDERAGE, OVERAGE, KYC_INCOMPLETE, SANCTIONED, HIGH_DEFAULT, DTI_CRITICAL

---

## 📊 5. Key Calculations

### DTI Ratio (Debt-to-Income)
```
DTI = (Monthly Obligations / Monthly Income) × 100
Scores: <20% = 100 | 20-35% = 85 | 35-50% = 60 | >50% = 20
```

### LTV Ratio (Loan-to-Value)
```
LTV = (Loan Amount / Total Assets) × 100
Scores: <60% = 100 | 60-75% = 85 | 75-85% = 60 | >85% = 30
```

### Monthly EMI (Equated Monthly Installment)
```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)
Where: P=Principal, r=Monthly Rate, n=Tenure
```

### Interest Rate Calculation
```
Base Rate = 7.5%
Adjustment = -0.5% to +1.0% based on credit score/risk
```

---

## 🔌 6. MCP Server Endpoints

### ApplicantDB
- `get_applicant(id)` → profile data
- `get_documents(id)` → document list
- `verify_employment(employer, years)` → employment status

### CreditHistoryDB
- `get_credit_score(id)` → 300-900
- `get_credit_history(id)` → detailed history
- `get_defaults(id)` → default records
- `get_bankruptcy(id)` → bankruptcy status

### RiskRulesDB
- `calculate_dti(income, obligations)` → DTI ratio
- `calculate_ltv(loan, assets)` → LTV ratio
- `assess_employment(type, years)` → stability score
- `calculate_emi(principal, rate, tenure)` → EMI amount

### NotificationSystem
- `send_notification(id, template, data)` → send email/SMS
- `create_audit_record(eval_id, event)` → log event
- `generate_letter(type, data, decision)` → create letter

---

## 🚀 7. API Endpoints

### Submit Application
```bash
POST /api/v1/loan/apply
Content-Type: application/json

{
  "applicant": {
    "name": "...",
    "age": 35,
    "annual_income": 2000000,
    "credit_score": 750,
    "employment_type": "employed",
    "employment_years": 10,
    "existing_liabilities": 500000,
    "total_assets": 1500000
  },
  "loan_details": {
    "amount": 5000000,
    "tenure_months": 60,
    "purpose": "home_loan"
  },
  "documents": ["aadhar", "pan", "salary_slip"]
}
```

### Check Status
```bash
GET /api/v1/loan/status/{application_id}
```

### Health Check
```bash
GET /api/v1/health
```

---

## 📈 8. Response Example

```json
{
  "evaluation_id": "EVAL12345",
  "application_id": "LN000001",
  "decision": "APPROVED",
  "final_score": 88.5,
  "risk_level": "LOW",
  "processing_time_ms": 52,
  "agent_results": [
    {"agent": "Document", "score": 95, "weight": 0.15},
    {"agent": "Credit", "score": 88, "weight": 0.30},
    {"agent": "Risk", "score": 76, "weight": 0.30},
    {"agent": "Compliance", "score": 100, "weight": 0.25}
  ],
  "approval_details": {
    "approved_amount": 5000000,
    "interest_rate": 7.85,
    "monthly_emi": 23542
  }
}
```

---

## 🧪 9. Testing Checklist

```python
# Unit tests
✓ Document agent: completeness, consistency, anomalies
✓ Credit agent: score calculation, history weighting
✓ Risk agent: DTI/LTV calculation, employment scoring
✓ Compliance agent: regulatory checks

# Integration tests
✓ Parallel agent execution (<100ms)
✓ Score synthesis (correct weighting)
✓ Decision logic (threshold accuracy)

# E2E tests
✓ Approved application flow
✓ Rejected application flow
✓ Manual review flow
✓ API rate limiting

# Performance tests
✓ Single app: <100ms
✓ 1000 apps: >80 apps/sec throughput
✓ Concurrent connections: 1000+
```

---

## 🔒 10. Security Checklist

```
✓ Input validation (type, range, format)
✓ Authentication & authorization (OAuth2)
✓ Rate limiting (10/min per IP)
✓ SQL injection prevention (parameterized queries)
✓ XSS protection (input sanitization)
✓ CORS configuration (whitelist domains)
✓ HTTPS only (TLS 1.2+)
✓ PII encryption (at rest and transit)
✓ Audit logging (all decisions recorded)
✓ Data retention (7 years for compliance)
```

---

## 🚨 11. Error Handling

```python
# Validation errors (400)
- Missing required fields
- Invalid data types
- Out of range values
- Duplicate applications

# Rate limit errors (429)
- Too many requests (>10/minute)

# Server errors (500)
- MCP server unavailable
- Database connection failed
- Unexpected agent error

# Retry strategy
- 3 retries for transient errors
- 5 second exponential backoff
- Circuit breaker for cascading failures
```

---

## 📊 12. Monitoring Metrics

```
Real-time Dashboard:
✓ Requests/second
✓ Average response time
✓ 95th percentile latency
✓ Error rate
✓ Approval rate (%)
✓ Manual review rate (%)
✓ Agent execution times
✓ MCP server health
✓ Database connection pool
✓ Message queue depth

Alerts:
- Response time > 200ms
- Error rate > 1%
- Any agent failure
- MCP server down
- Database unavailable
```

---

## 🔄 13. Data Flow Example

```
1. User submits form (Streamlit)
   ↓
2. API receives + validates (FastAPI)
   ↓
3. Orchestrator routes to agents (LangGraph)
   ↓
4. 4 agents execute in parallel (100ms)
   ├─ Document: Check completeness (15ms)
   ├─ Credit: Fetch bureau data (20ms)
   ├─ Risk: Calculate ratios (15ms)
   └─ Compliance: Verify rules (18ms)
   ↓
5. Scores synthesized (5ms)
   ├─ 95 × 0.15 = 14.25
   ├─ 88 × 0.30 = 26.40
   ├─ 76 × 0.30 = 22.80
   └─ 100 × 0.25 = 25.00
   └─ TOTAL = 88.5
   ↓
6. Decision made (3ms)
   └─ 88.5 ≥ 70 → APPROVED
   ↓
7. Approval letter generated (5ms)
   ↓
8. Notification sent (10ms)
   ↓
9. Audit log recorded (5ms)
   ↓
10. Response returned (52ms total)
```

---

## 💡 14. Troubleshooting

### Issue: Slow response (>200ms)
**Debug**: 
```bash
# Check agent timing in logs
grep "processing_time" audit_logs/*.log

# Profile individual agents
python -m cProfile -o profile.prof main.py
```
**Fix**: Increase cache, reduce MCP calls, optimize DB queries

### Issue: High rejection rate (>60%)
**Debug**: 
```python
# Analyze scoring distribution
results = analyze_decisions(last_100_apps)
print(results["score_distribution"])
print(results["reasons_for_rejection"])
```
**Fix**: Adjust weights, review agent logic, check for data quality issues

### Issue: Inconsistent decisions (same app, different results)
**Debug**: Check for non-deterministic scoring, randomness in agent logic
**Fix**: Ensure idempotent calculations, add feature pinning

---

## 🎯 15. Common Code Patterns

### Execute Async Operation
```python
async def evaluate_loan(app):
    results = await asyncio.gather(
        doc_agent.execute(app),
        credit_agent.execute(app),
        risk_agent.execute(app),
        compliance_agent.execute(app)
    )
    return synthesize(results)
```

### Calculate Weighted Score
```python
final_score = sum(
    result["score"] * weights[result["name"]]
    for result in agent_results
)
```

### Make Decision
```python
if final_score >= 70 and not critical_flags:
    decision = "APPROVED"
elif final_score >= 45:
    decision = "MANUAL_REVIEW"
else:
    decision = "REJECTED"
```

### Create Audit Record
```python
audit_record = {
    "timestamp": datetime.utcnow().isoformat(),
    "evaluation_id": eval_id,
    "decision": decision,
    "score": final_score,
    "agent_results": agent_results
}
save_to_audit_log(audit_record)
```

---

## 📚 16. Key Files

| File | Purpose |
|------|---------|
| `core/models.py` | Data models & enums |
| `agents/base_agent.py` | Abstract agent class |
| `agents/document_agent.py` | Document verification |
| `agents/credit_agent.py` | Credit analysis |
| `agents/risk_agent.py` | Risk assessment |
| `agents/compliance_agent.py` | Regulatory compliance |
| `services/orchestrator.py` | LangGraph orchestrator |
| `api/gateway.py` | FastAPI endpoints |
| `main.py` | Entry point |
| `tests/test_*.py` | Test suite |

---

## ⚡ 17. Performance Tuning

```python
# Connection pooling
AsyncConnectionPool(max_size=100)

# Caching
@lru_cache(maxsize=10000)
def get_credit_score(id): ...

# Batch processing
batch_size = 100
for batch in chunked(applications, batch_size):
    results = await process_batch(batch)

# Compression
gzip_response(result, compression_level=6)

# Parallel MCP calls
mcp_results = await asyncio.gather(*mcp_tasks)
```

---

## 🔗 18. Integration Points

**Inbound**:
- Streamlit UI → FastAPI gateway
- Mobile app → FastAPI gateway

**Outbound**:
- MCP servers (credit bureau, KYC, notification)
- Email service (Gmail/SendGrid)
- SMS service (Twilio)
- Audit database (PostgreSQL)

---

## 📞 19. Quick Contacts

| Role | Contact | SLA |
|------|---------|-----|
| Tech Lead | tech-lead@rsbank.com | 1hr |
| DevOps | devops@rsbank.com | 30min |
| Compliance | compliance@rsbank.com | 4hr |
| Security | security@rsbank.com | 2hr |

---

## ✨ 20. Key Success Factors

1. **Parallel Execution** - All agents run concurrently (not sequential)
2. **Weighted Scoring** - Proper weight distribution (doc 15%, credit 30%, risk 30%, compliance 25%)
3. **Fast MCP Calls** - Cache frequently accessed data
4. **Clear Decision Logic** - Simple thresholds (approved ≥70, review 45-70, rejected <45)
5. **Comprehensive Audit Trail** - Track every decision for compliance
6. **Error Handling** - Graceful degradation with fallback scores
7. **Monitoring** - Real-time alerts for SLA breaches
8. **Documentation** - Clear explanations for every decision

---

**Last Updated**: July 3, 2026  
**Version**: 1.0  
**Status**: ✅ Ready for Production
