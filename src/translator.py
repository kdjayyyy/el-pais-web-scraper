# import os
# import requests
# from typing import List

# RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
# RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# def translate_with_rapidapi_single(
#     text: str, from_lang: str = "es", to_lang: str = "en"
# ) -> str:
#     if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
#         raise RuntimeError("Set the environment variables!")

#     url = f"https://{RAPIDAPI_HOST}/t"
#     payload = {"from": from_lang, "to": to_lang, "q": text}
#     headers = {
#         "content-type": "application/json",
#         "x-rapidapi-key": RAPIDAPI_KEY,
#         "x-rapidapi-host": RAPIDAPI_HOST,
#     }
#     resp = requests.post(url, json=payload, headers=headers, timeout=20)
    
#     resp.raise_for_status()
#     data = resp.json()

#     if isinstance(data, list) and len(data) > 0:
#         return str(data[0])

#     # Try common response shapes
#     if isinstance(data, dict):
#         for k in (
#             "translated_text",
#             "translatedText",
#             "result",
#             "translation",
#             "translated",
#         ):
#             if k in data:
#                 return data[k]
#         if "data" in data and isinstance(data["data"], dict):
#             d = data["data"]
#             if (
#                 "translations" in d
#                 and isinstance(d["translations"], list)
#                 and d["translations"]
#             ):
#                 if "translatedText" in d["translations"][0]:
#                     return d["translations"][0]["translatedText"]
#         if isinstance(data.get("text"), str):
#             return data.get("text")
#     return str(data)


# def translate_many(
#     texts: List[str], from_lang: str = "es", to_lang: str = "en"
# ) -> List[str]:
#     out = []
#     for t in texts:
#         if not t:
#             out.append("")
#             continue
#         out.append(
#             translate_with_rapidapi_single(t, from_lang=from_lang, to_lang=to_lang)
#         )
#     return out


import os
import requests
import time
from typing import List

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")


def translate_with_rapidapi_single(
    text: str, from_lang: str = "es", to_lang: str = "en", retries: int = 3
) -> str:
    if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
        raise RuntimeError("Set the environment variables!")

    url = f"https://{RAPIDAPI_HOST}/t"
    payload = {"from": from_lang, "to": to_lang, "e": "", "q": text}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            
            # If rate limited, wait and retry
            if resp.status_code == 429:
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                print(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{retries}")
                time.sleep(wait_time)
                continue
            
            resp.raise_for_status()
            data = resp.json()

            # The API returns a list with the translation
            if isinstance(data, list) and len(data) > 0:
                return str(data[0])

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

            return str(data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{retries}")
                time.sleep(wait_time)
            else:
                raise
    
    # If all retries failed
    raise Exception("Translation failed after all retries")


def translate_many(
    texts: List[str], from_lang: str = "es", to_lang: str = "en", delay: float = 0.5
) -> List[str]:
    """Translate multiple texts with delay between requests to avoid rate limiting."""
    out = []
    for i, t in enumerate(texts):
        if t:  # Only translate non-empty strings
            try:
                translated = translate_with_rapidapi_single(t, from_lang=from_lang, to_lang=to_lang)
                out.append(translated)
            except Exception as e:
                print(f"Translation failed for '{t}': {e}")
                out.append(t)  # Use original text as fallback
        else:
            out.append("")
        
        # Add delay between requests (except for last one)
        if i < len(texts) - 1:
            time.sleep(delay)
    
    return out