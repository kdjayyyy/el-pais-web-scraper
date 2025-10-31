import os
import re
import requests
from pathlib import Path
from typing import Optional, List


def download_image(url: str, dest_folder: str = "images") -> Optional[str]:
    """Download image at `url` to `dest_folder`. Returns local path or None."""
    if not url:
        return None
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    filename = os.path.basename(url.split("?")[0])
    local_path = Path(dest_folder) / filename
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        local_path.write_bytes(r.content)
        return str(local_path)
    except Exception as e:
        print(f"[utils] failed to download image {url}: {e}")
        return None


def normalize_and_tokenize(text: str) -> List[str]:
    """Lowercase, remove punctuation, and split into words."""
    t = (text or "").lower()
    t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
    return [w for w in t.split() if w]
