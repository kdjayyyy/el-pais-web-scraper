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
    """Set up Chrome driver with Spanish language preference."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    # Request Spanish content
    opts.add_experimental_option("prefs", {"intl.accept_languages": "es"})
    
    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"Failed to auto-download chromedriver: {e}")
        print("Falling back to system chromedriver")
        service = Service()  # Try system PATH
    
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1200, 900)
    return driver

def scrape_first_n_opinion_articles(driver: webdriver.Chrome, n: int = 5) -> List[dict]:
    """Scrape first n articles from El País Opinion section."""
    opinion_url = "https://elpais.com/opinion/"
    driver.get(opinion_url)
    time.sleep(2)

    # Find all article links - look for h2/h3 with links (article headlines)
    # Store both href and the title text from the homepage
    anchors = driver.find_elements(By.CSS_SELECTOR, "article h2 a, article h3 a")
    article_data = []  # List of (href, homepage_title) tuples

    for a in anchors:
        h = a.get_attribute("href")
        
        # Try multiple ways to get the title from homepage
        homepage_title = a.text.strip()
        
        # If link text is empty, try getting text from parent h2/h3
        if not homepage_title:
            try:
                parent = a.find_element(By.XPATH, "./..")  # Parent element
                homepage_title = parent.text.strip()
            except Exception:
                pass
        
        # If still empty, try aria-label or title attribute
        if not homepage_title:
            homepage_title = a.get_attribute("aria-label") or a.get_attribute("title") or ""
            homepage_title = homepage_title.strip()
        
        # Filter: must contain /opinion/ and have date pattern (YYYY-MM-DD) indicating it's an article
        if h and "/opinion/" in h:
            # Skip section pages - they end with just /opinion/something/
            # Articles have dates like /opinion/2025-11-01/...
            if any(char.isdigit() for char in h.split("/opinion/")[-1][:20]):
                # Check if already added
                if not any(href == h for href, _ in article_data):
                    article_data.append((h, homepage_title))
        
        if len(article_data) >= n:
            break

    results = []

    for link, homepage_title in article_data[:n]:
        print(f"Scraping: {link}")
        print(f"  Homepage title: '{homepage_title}'")
        driver.get(link)
        
        # Wait for page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except Exception:
            pass
        
        time.sleep(2)  # Additional wait for JS

        # Title - try multiple selectors with fallbacks
        title = ""
        try:
            title_el = driver.find_element(By.TAG_NAME, "h1")
            title = title_el.text.strip()
            print(f"  Page h1: '{title}'")
            
            # If h1 is empty, use homepage title as fallback
            if not title and homepage_title:
                title = homepage_title
                print(f"  Using homepage title: '{title}'")
            elif not title:
                # Last resort: try og:title meta tag
                try:
                    meta = driver.find_element(By.XPATH, "//meta[@property='og:title']")
                    title = meta.get_attribute("content").strip()
                    # Remove site name if present (usually after | or -)
                    if "|" in title:
                        title = title.split("|")[0].strip()
                    elif " - " in title:
                        title = title.split(" - ")[0].strip()
                    print(f"  Using og:title: '{title}'")
                except Exception:
                    pass
        except Exception as e:
            print(f"  No h1 found: {e}")
            # Use homepage title as fallback
            if homepage_title:
                title = homepage_title
                print(f"  Using homepage title: '{title}'")
            else:
                # Try og:title as last resort
                try:
                    meta = driver.find_element(By.XPATH, "//meta[@property='og:title']")
                    title = meta.get_attribute("content").strip()
                    if "|" in title:
                        title = title.split("|")[0].strip()
                    elif " - " in title:
                        title = title.split(" - ")[0].strip()
                    print(f"  Using og:title: '{title}'")
                except Exception:
                    title = ""

        # Body
        body = ""
        try:
            article_tag = driver.find_element(By.CSS_SELECTOR, "article")
            ps = article_tag.find_elements(By.TAG_NAME, "p")
            body = "\n\n".join([p.text for p in ps if p.text.strip()])
        except Exception:
            try:
                ps = driver.find_elements(By.CSS_SELECTOR, "main p")
                body = "\n\n".join([p.text for p in ps if p.text.strip()])
            except Exception:
                body = ""

        # Image
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
    """Analyze translated headers for repeated words."""
    words = []
    for th in translated_headers:
        if th:  # Skip empty strings
            words.extend(normalize_and_tokenize(th))
    
    counts = Counter(words)
    repeated_more_than_two = {w: c for w, c in counts.items() if c > 2}
    
    return {
        "counts": counts,
        "repeated_more_than_two": repeated_more_than_two
    }


def main(headless: bool = True, translate: bool = True):
    """Main function to scrape, translate, and analyze articles."""
    driver = setup_local_driver(headless=headless)
    try:
        scraped = scrape_first_n_opinion_articles(driver, n=5)
        titles_es = [r["title_es"] for r in scraped]

        if translate:
            translated = translate_many(titles_es, from_lang="es", to_lang="en")
        else:
            translated = ["" for _ in titles_es]

        # Print results
        for i, r in enumerate(scraped, start=1):
            print(f"\n--- Article {i} ---")
            print("URL:", r["url"])
            print("Title (ES):", r["title_es"])
            print("Title (EN):", translated[i - 1])
            print("Image local:", r["image_local"])

        # Analyze translated headers
        analysis = analyze_translated_headers(translated)
        print("\nWords repeated more than twice:")
        if analysis["repeated_more_than_two"]:
            for w, c in analysis["repeated_more_than_two"].items():
                print(f"{w}: {c}")
        else:
            print("No words repeated more than twice")

        return scraped, translated, analysis
    finally:
        driver.quit()


if __name__ == "__main__":
    headless_env = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
    main(headless=headless_env, translate=True)