from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

# Optional: Groq SDK; fall back to simple requests if not available
try:
    from groq import Groq
except Exception:  # pragma: no cover
    Groq = None  # type: ignore

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
PROM_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100")
JAEGER_API = os.getenv("JAEGER_API", "http://jaeger:16686/api")

app = FastAPI(title="AI Service", version="1.0.0")


class ChatRequest(BaseModel):
    query: str
    context: dict | None = None


class IncidentContext(BaseModel):
    time_range: str = "1h"
    services: list[str] | None = None


import re

def _clean_markdown(text: str) -> str:
    """Clean up HTML tags and ensure proper markdown formatting"""
    # Replace <br> tags with proper line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)
    # Replace other common HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()

def _llm(prompt: str, max_tokens: int = 400, temperature: float = 0.2) -> str:
    if not GROQ_API_KEY:
        return "AI disabled: set GROQ_API_KEY to enable responses."
    if Groq:
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": """You are a Site Reliability Engineering AI assistant. Be EXTREMELY CONCISE. Provide only essential information.

FORMATTING RULES:
1. Use proper markdown tables with | separators
2. Keep responses SHORT - 3-5 sentences max
3. Tables should be compact with only critical columns
4. No emojis, no special unicode characters
5. Use bullet points (-) for lists, max 3-4 items
6. Use ## for section headers
7. Never use HTML tags (no <br>, <b>, etc)
8. Use plain text for status indicators (OK, ERROR, WARNING)
9. NO lengthy explanations - be direct and actionable
10. Skip introductory phrases - get straight to the point"""},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result = resp.choices[0].message.content or ""
        return _clean_markdown(result)
    # Fallback (no SDK). Keep disabled to avoid leaking keys via raw HTTP by default.
    return "AI client not available. Install groq SDK."


def _prom(query: str) -> dict:
    try:
        r = requests.get(f"{PROM_URL}/api/v1/query", params={"query": query}, timeout=8)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _loki(query: str, limit: int = 50) -> dict:
    try:
        r = requests.get(
            f"{LOKI_URL}/loki/api/v1/query",
            params={"query": query, "limit": limit},
            timeout=8,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _jaeger_services() -> dict:
    try:
        r = requests.get(f"{JAEGER_API}/services", timeout=8)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai-service"}


@app.post("/chat")
def chat(req: ChatRequest):
    ctx = ", ".join(req.context.get("services", [])) if req.context else ""
    prompt = f"User asked: {req.query}\n\nServices: {ctx if ctx else 'orders, users, payments'}.\n\nAnswer in 3-4 sentences max. Use a table if showing data."
    answer = _llm(prompt, max_tokens=300)
    return {"answer": answer}


@app.post("/summarize")
def summarize(ctx: IncidentContext):
    logs = _loki('{job=~"orders-service|users-service|payments-service"}', limit=50)
    metrics = _prom("sum by (job)(rate(http_requests_total[5m]))")
    
    prompt = (
        f"Incident summary for last {ctx.time_range}.\n\n"
        f"METRICS: {str(metrics)[:300]}\n"
        f"LOGS: {str(logs)[:400]}\n\n"
        "Provide 4-5 bullet points covering: affected services, symptoms, status, next steps."
    )
    summary = _llm(prompt, max_tokens=250, temperature=0.1)
    return {"summary": summary}


@app.post("/rca")
def rca(ctx: IncidentContext):
    logs = _loki('{job=~"orders-service|users-service|payments-service"}', limit=100)
    metrics = _prom("sum by (job)(rate(http_requests_total[5m]))")
    cpu_metrics = _prom("process_cpu_seconds_total")
    error_metrics = _prom("rate(http_requests_total{status=~'5..'}[5m])")
    
    prompt = (
        f"RCA for {ctx.time_range} incident.\n\n"
        f"REQUESTS: {str(metrics)[:300]}\n"
        f"CPU: {str(cpu_metrics)[:300]}\n"
        f"ERRORS: {str(error_metrics)[:300]}\n"
        f"LOGS: {str(logs)[:400]}\n\n"
        "Provide:\n"
        "## Suspected Service\n"
        "[name] (confidence: X%)\n\n"
        "## Evidence\n"
        "- [3 key points max]\n\n"
        "## Actions\n"
        "1. [immediate]\n"
        "2. [next step]\n"
        "3. [prevention]\n"
    )
    answer = _llm(prompt, max_tokens=350, temperature=0.1)
    return {"rca": answer}


class AdviceInput(BaseModel):
    service: str
    anomaly: str
    context: dict | None = None


@app.post("/advice")
def advice(inp: AdviceInput):
    prompt = (
        f"As an SRE AI, recommend the BEST remediation action for this situation:\n\n"
        f"SERVICE: {inp.service}\n"
        f"ANOMALY: {inp.anomaly}\n"
        f"CONTEXT: {inp.context}\n\n"
        "Available actions: restart_container, scale_up, alert\n\n"
        "Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "action": "restart_container|scale_up|alert",\n'
        '  "confidence": 0.XX (decimal 0-1),\n'
        '  "rationale": "brief explanation in 1-2 sentences",\n'
        '  "expected_impact": "what will happen",\n'
        '  "risk_level": "low|medium|high"\n'
        "}\n"
    )
    answer = _llm(prompt, max_tokens=400, temperature=0.1)
    return {"advice": answer}


