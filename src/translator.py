import os
import requests
from typing import List

RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")


def translate_with_rapidapi_single(
    text: str, from_lang: str = "es", to_lang: str = "en"
) -> str:
    if not RAPID_API_KEY or not RAPID_API_HOST:
        raise RuntimeError("Set the environment variables!")

    url = f"https://{RAPID_API_HOST}/translate"
    payload = {"from": from_lang, "to": to_lang, "q": text}
    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # Try common response shapes
    if isinstance(data, dict):
        for k in (
            "translated_text",
            "translatedText",
            "result",
            "translation",
            "translated",
        ):
            if k in data:
                return data[k]
        if "data" in data and isinstance(data["data"], dict):
            d = data["data"]
            if (
                "translations" in d
                and isinstance(d["translations"], list)
                and d["translations"]
            ):
                if "translatedText" in d["translations"][0]:
                    return d["translations"][0]["translatedText"]
        if isinstance(data.get("text"), str):
            return data.get("text")
    # fallback: return raw json as string
    return str(data)


def translate_many(
    texts: List[str], from_lang: str = "es", to_lang: str = "en"
) -> List[str]:
    out = []
    for t in texts:
        if not t:
            out.append("")
            continue
        out.append(
            translate_with_rapidapi_single(t, from_lang=from_lang, to_lang=to_lang)
        )
    return out
