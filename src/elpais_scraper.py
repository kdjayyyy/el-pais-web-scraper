import os
import time
from collections import Counter
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from .utils import download_image, normalize_and_tokenize
from .translator import translate_many

def setup_local_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    # Request Spanish content
    opts.add_experimental_option("prefs", {"intl.accept_languages": "es"})
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1200, 900)
    return driver



def scrape_first_n_opinion_articles(driver: webdriver.Chrome, n: int = 5) -> List[dict]:
    opinion_url = "https://elpais.com/opinion/"
    driver.get(opinion_url)
    time.sleep(2)

    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/opinion/']")
    hrefs = []
    for a in anchors:
        h = a.get_attribute("href")
        if h and "/opinion/" in h and h not in hrefs:
            hrefs.append(h)
        if len(hrefs) >= n * 5:
            break

    article_links = hrefs[:n]
    results = []
    for link in article_links:
        driver.get(link)
        time.sleep(1)
        # title
        try:
            title_el = driver.find_element(By.TAG_NAME, "h1")
            title = title_el.text.strip()
        except Exception:
            title = ""
        # body
        body = ""
        try:
            article_tag = driver.find_element(By.CSS_SELECTOR, "article")
            ps = article_tag.find_elements(By.TAG_NAME, "p")
            body = "\n\n".join([p.text for p in ps if p.text.strip()])
        except Exception:
            ps = driver.find_elements(By.CSS_SELECTOR, "main p")
            body = "\n\n".join([p.text for p in ps if p.text.strip()])
        # image
        image_url = None
        try:
            meta = driver.find_element(By.XPATH, "//meta[@property='og:image']")
            image_url = meta.get_attribute("content")
        except Exception:
            try:
                img = driver.find_element(By.CSS_SELECTOR, "article figure img")
                image_url = img.get_attribute("src")
            except Exception:
                image_url = None
        image_local = download_image(image_url) if image_url else None

        results.append({
            "url": link,
            "title_es": title,
            "body_es": body,
            "image_url": image_url,
            "image_local": image_local,
        })

    return results


def analyze_translated_headers(translated_headers: List[str]) -> dict:
    words = []
    for th in translated_headers:
        words.extend(normalize_and_tokenize(th))
    counts = Counter(words)
    repeated_more_than_two = {w: c for w, c in counts.items() if c > 2}
    return {"counts": counts, "repeated_more_than_two": repeated_more_than_two}


def main(headless: bool = True, translate: bool = True):
    driver = setup_local_driver(headless=headless)
    try:
        scraped = scrape_first_n_opinion_articles(driver, n=5)
        titles_es = [r["title_es"] for r in scraped]

        if translate:
            translated = translate_many(titles_es, from_lang="es", to_lang="en")
        else:
            translated = ["" for _ in titles_es]

        for i, r in enumerate(scraped, start=1):
            print(f"\n--- Article {i} ---")
            print("URL:", r["url"])
            print("Title (ES):", r["title_es"])
            print("Title (EN):", translated[i - 1])
            print("Image local:", r["image_local"])

        analysis = analyze_translated_headers(translated)
        print("\nWords repeated more than twice:")
        for w, c in analysis["repeated_more_than_two"].items():
            print(w, c)

        return scraped, translated, analysis
    finally:
        driver.quit()


if __name__ == "__main__":
    headless_env = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
    main(headless=headless_env, translate=True)
