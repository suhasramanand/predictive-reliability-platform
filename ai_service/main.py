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
                {"role": "system", "content": "You are a Site Reliability Engineering AI assistant. Provide concise, actionable responses focused on metrics, observability, and remediation. Use proper markdown formatting with tables, bullet points, and line breaks. NEVER use HTML tags like <br> - use markdown formatting instead."},
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
    prompt = req.query
    if req.context:
        prompt += "\nContext:\n" + str(req.context)
    answer = _llm(prompt)
    return {"answer": answer}


@app.post("/summarize")
def summarize(ctx: IncidentContext):
    # Simple heuristic summary assembled from observability backends
    metrics = _prom(f"rate(http_requests_total[5m])")
    services = _jaeger_services()
    logs = _loki('{job="orders-service"}')
    prompt = (
        f"Analyze this {ctx.time_range} incident data and provide a brief summary (max 200 words).\n\n"
        f"METRICS: {str(metrics)[:800]}\n"
        f"SERVICES: {str(services)[:300]}\n"
        f"LOGS: {str(logs)[:600]}\n\n"
        "Format your response using proper markdown:\n"
        "## Key Signals\n"
        "- [what metrics/logs show]\n\n"
        "## Impacted Services\n"
        "- [list services]\n\n"
        "## Suspected Cause\n"
        "[likely root cause]\n\n"
        "## Recommended Actions\n"
        "1. [action 1]\n"
        "2. [action 2]\n"
        "3. [action 3]\n"
    )
    answer = _llm(prompt, max_tokens=300)
    return {"summary": answer}


@app.post("/rca")
def rca(ctx: IncidentContext):
    logs = _loki('{job=~"orders-service|users-service|payments-service"}', limit=100)
    metrics = _prom("sum by (job)(rate(http_requests_total[5m]))")
    cpu_metrics = _prom("process_cpu_seconds_total")
    error_metrics = _prom("rate(http_requests_total{status=~'5..'}[5m])")
    
    prompt = (
        f"Perform root cause analysis for a {ctx.time_range} incident window.\n\n"
        f"REQUEST RATES: {str(metrics)[:500]}\n"
        f"CPU METRICS: {str(cpu_metrics)[:500]}\n"
        f"ERROR RATES: {str(error_metrics)[:500]}\n"
        f"LOG SAMPLE: {str(logs)[:700]}\n\n"
        "Analyze the data and provide a structured RCA report in markdown format:\n\n"
        "## Root Cause Analysis\n\n"
        "### Suspected Service\n"
        "[service name or component]\n\n"
        "### Confidence Level\n"
        "[confidence percentage]\n\n"
        "### Key Evidence\n"
        "- [evidence 1]\n"
        "- [evidence 2]\n"
        "- [evidence 3]\n\n"
        "### Likely Causes\n"
        "1. [cause 1]\n"
        "2. [cause 2]\n"
        "3. [cause 3]\n\n"
        "### Recommended Actions\n"
        "1. [immediate action]\n"
        "2. [investigation step]\n"
        "3. [prevention measure]\n"
    )
    answer = _llm(prompt, max_tokens=400, temperature=0.1)
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
    answer = _llm(prompt, max_tokens=250, temperature=0.1)
    return {"advice": answer}


