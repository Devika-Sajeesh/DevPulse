import os, json, httpx
from dotenv import load_dotenv

load_dotenv()
print("DEBUG: GROQ_KEY =", os.getenv("GROQ_API_KEY"))


GROQ_KEY = os.getenv("GROQ_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

# --- Utility: truncate long text ---
def truncate(text: str, max_chars: int = 2000) -> str:
    if not text:
        return ""
    return text[:max_chars] + ("..." if len(text) > max_chars else "")

async def generate_summary(radon: str, cloc: str, pylint: str):
    if not (GROQ_KEY or OPENAI_KEY):
        return {"error": "No API key set. Please configure GROQ_API_KEY or OPENAI_API_KEY."}

    # ✅ Only send trimmed content
    prompt = (
        "Summarize the following analysis into JSON with keys:\n"
        "complexity (radon), quality (pylint), maintainability (cloc), "
        "and recommendations (list). Keep it short.\n\n"
        f"Radon (trimmed):\n{truncate(radon)}\n\n"
        f"CLOC (trimmed):\n{truncate(cloc)}\n\n"
        f"Pylint (trimmed):\n{truncate(pylint)}"
    )

    api_url = (
        "https://api.groq.com/openai/v1/chat/completions" if GROQ_KEY
        else "https://api.openai.com/v1/chat/completions"
    )
    headers = {
        "Authorization": f"Bearer {GROQ_KEY or OPENAI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(api_url, json=payload, headers=headers)
        data = r.json()

    # Defensive parsing
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        return {"error": f"Bad response from AI: {data}"}

    # Extract JSON safely
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end == -1:
        return {"raw": content}

    try:
        return json.loads(content[start:end+1])
    except Exception:
        return {"raw": content, "error": "Invalid JSON from AI"}
