import os, json, httpx

GROQ_KEY = os.getenv("GROQ_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

async def generate_summary(radon: str, cloc: str, pylint: str):
    if not (GROQ_KEY or OPENAI_KEY):
        return {"error": "No API key set"}

    prompt = (
        "Summarize into JSON with keys: complexity, quality, maintainability, "
        "recommendations (list). Keep it short.\n\n"
        f"Radon:\n{radon}\n\nCloc:\n{cloc}\n\nPylint:\n{pylint}"
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

    content = data["choices"][0]["message"]["content"]
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end == -1:
        return {"raw": content}

    try:
        return json.loads(content[start:end+1])
    except Exception:
        return {"raw": content, "error": "Invalid JSON from AI"}
