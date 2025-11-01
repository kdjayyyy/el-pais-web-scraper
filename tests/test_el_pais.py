import os
import pytest
from src.browserstack_runner import get_remote_driver, EXAMPLE_CAPS
from src.elpais_scraper import scrape_first_n_opinion_articles

@pytest.mark.parametrize("bstack_options", EXAMPLE_CAPS)
def test_scrape_opinion_on_browserstack(bstack_options):
    user = os.getenv("BROWSERSTACK_USERNAME")
    key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    if not user or not key:
        pytest.skip("BrowserStack credentials not set")

    driver = get_remote_driver(bstack_options=bstack_options)
    try:
        articles = scrape_first_n_opinion_articles(driver, n=5)
        assert isinstance(articles, list)
        assert len(articles) == 5
        for a in articles:
            # Basic sanity checks
            assert "title_es" in a
            assert "body_es" in a
            print("TITLE_ES:", (a.get("title_es") or "")[:120])
    finally:
        driver.quit()
