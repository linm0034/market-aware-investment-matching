
````markdown
# Market-aware Investment Opportunity Matching System  
**Agentic GenAI + RAG + Scenario-based Evaluation**

A market-aware GenAI system that matches **investment opportunities** to **client profiles** under different **market regimes**, producing **evidence-backed, auditable recommendations** instead of static or black-box ranking.

> ⚠️ Disclaimer: This project is for educational and prototyping purposes only.  
> It does not constitute financial advice and does not guarantee investment returns.


---

## Key Features

- **Market-aware recommendations**  
  Recommendations adapt across different market regimes (e.g., rising vs falling rates).

- **Suitability screening**  
  Products violating client constraints (risk tolerance, liquidity, ESG / no-derivatives) are filtered before recommendation.

- **RAG-grounded explanations**  
  All recommendation rationales are supported by retrieved evidence from product documents.

- **Agentic decision workflow**  
  Recommendation reasoning and audit/compliance checks are separated into distinct agents.

- **REST API service**  
  A `/recommend` endpoint supports both serving and offline batch evaluation.

---

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic  
- **Agentic AI**: LangChain, OpenAI API  
- **RAG**: OpenAI Embeddings, FAISS vector search  
- **Evaluation**: Scenario-based simulation, batch REST evaluation  

---

## System Architecture (Conceptual)

```text
Client Profile + Constraints
            ↓
   Suitability Filtering (Rules)
            ↓
     Candidate Products
            ↓
   RAG Evidence Retrieval
            ↓
 Recommendation Agent (LLM)
            ↓
     Audit / Compliance Agent
            ↓
   Final Recommendations
````

---

## Repository Structure

```text
app/
  main.py            # FastAPI entry point and /recommend endpoint
  agents.py          # recommendation and audit agents (LangChain)
  rag.py             # FAISS vectorstore build/load and retrieval
  rules.py           # suitability filtering logic
data/
  opportunities.csv  # structured product metadata
  docs/              # investment product documents (RAG source)
  clients.json       # simulated client profiles for evaluation
eval/
  offline_eval.py    # scenario-based batch evaluation script
```

---

## Setup

### 1) Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key
```

> `.env` is intentionally excluded from version control.

---

## Run the API

Start the service:

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Swagger UI:

* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Example Request

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "client_id": "c001",
      "risk_tolerance": 2,
      "horizon_months": 24,
      "goal": "Income",
      "liquidity_need": "High",
      "constraints": ["ESG-only", "No-derivatives"]
    },
    "market": {
      "interest_rate_trend": "rising",
      "volatility_level": "high"
    },
    "top_k": 3
  }'
```

---

## Evaluation

The system is evaluated using **scenario-based batch testing** via the same REST endpoint used for serving.

### Methodology

* **Clients**: 20 simulated client profiles
* **Market scenarios**: 3 regimes (e.g., rising / stable / falling rates with different volatility levels)
* **Total runs**: `20 clients × 3 scenarios = 60` end-to-end API calls

### Metrics

* **Evidence coverage rate**
  Percentage of runs where recommendations include non-empty RAG evidence.

* **Avg recommendations per run**
  Average number of recommended products returned per request.

* **Avg rejected per run**
  Average number of products filtered out by suitability rules.

* **Market-sensitive Top-1 ratio**
  For each client, whether the Top-1 recommendation changes across market scenarios.

### Results

```
Total runs: 60
Evidence coverage rate: 100.00%
Avg recommendations per run: 2.90
Avg rejected per run: 11.00
Market-sensitive top1 ratio: 65.00%
```

### Run evaluation locally

```bash
uvicorn app.main:app --reload --port 8000
python eval/offline_eval.py
```

---

## Notes & Limitations

* Market signals and client profiles are simplified for prototyping.
* Real-world deployment would require:

  * richer and real-time market data feeds
  * stricter governance, logging, and approval workflows
  * enhanced monitoring and access control
  * secure key management and model risk controls

```

