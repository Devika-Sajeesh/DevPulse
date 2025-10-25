import os, json
from fastapi import Request

def load_translations(lang: str):
    lang_file = os.path.join("backend", "locales", f"{lang}.json")
    if not os.path.exists(lang_file):
        lang_file = os.path.join("backend", "locales", "en.json")  # fallback
    with open(lang_file, encoding="utf-8") as f:
        return json.load(f)

async def get_translation(request: Request):
    lang = request.query_params.get("lang") or request.headers.get("Accept-Language", "en").split(",")[0]
    lang = lang.split("-")[0]  # handle cases like "en-US"
    return load_translations(lang)
