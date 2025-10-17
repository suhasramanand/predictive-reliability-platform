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


def _llm(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "AI disabled: set GROQ_API_KEY to enable responses."
    if Groq:
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": "You are an SRE AI assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        return resp.choices[0].message.content or ""
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
        "Summarize incident context across metrics, logs, and traces. "
        f"Time range: {ctx.time_range}.\n"
        f"Metrics sample: {str(metrics)[:1200]}\n"
        f"Jaeger services: {str(services)[:400]}\n"
        f"Logs sample: {str(logs)[:800]}\n"
        "Provide: key signals, impacted services, suspected root cause, recommended next actions."
    )
    answer = _llm(prompt)
    return {"summary": answer}


@app.post("/rca")
def rca(ctx: IncidentContext):
    logs = _loki('{job=~"orders-service|users-service|payments-service"}', limit=100)
    metrics = _prom("sum by (job)(rate(http_requests_total[5m]))")
    prompt = (
        "Given logs clusters and request rates by service, identify the most likely failing subsystem "
        "and rationale. Return JSON with fields: {suspect_service, confidence, reasons}.\n"
        f"Logs: {str(logs)[:1200]}\nMetrics: {str(metrics)[:600]}\n"
    )
    answer = _llm(prompt)
    return {"rca": answer}


class AdviceInput(BaseModel):
    service: str
    anomaly: str
    context: dict | None = None


@app.post("/advice")
def advice(inp: AdviceInput):
    prompt = (
        f"Service: {inp.service}\nAnomaly: {inp.anomaly}\nContext: {inp.context}\n"
        "Recommend one remediation action among: restart_container, scale_up, alert."
        " Explain briefly and return JSON {action, rationale}."
    )
    answer = _llm(prompt)
    return {"advice": answer}


