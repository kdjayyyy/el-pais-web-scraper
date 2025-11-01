import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .elpais_scraper import scrape_first_n_opinion_articles, analyze_translated_headers
from .translator import translate_many


def get_browserstack_driver(capabilities: dict) -> webdriver.Remote:
    """Create a BrowserStack Remote WebDriver."""
    bs_username = os.getenv("BROWSERSTACK_USERNAME")
    bs_access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    
    if not bs_username or not bs_access_key:
        raise ValueError("BrowserStack credentials not found in environment variables")
    
    url = f"https://{bs_username}:{bs_access_key}@hub-cloud.browserstack.com/wd/hub"
    
    browser_name = capabilities.get("browserName", "").lower()
    
    # Create appropriate options object based on browser
    if "chrome" in browser_name:
        options = ChromeOptions()
        # Set Spanish language preference for Chrome
        options.set_capability("prefs", {"intl.accept_languages": "es"})
    elif "firefox" in browser_name:
        options = FirefoxOptions()
        # Set Spanish language preference for Firefox
        options.set_preference("intl.accept_languages", "es")
    elif "safari" in browser_name:
        options = SafariOptions()
    else:
        options = ChromeOptions()  # Default to Chrome options
    
    # Add all BrowserStack capabilities
    for key, value in capabilities.items():
        options.set_capability(key, value)
    
    # Set Spanish language at BrowserStack level too
    options.set_capability("browserstack.language", "es")
    
    return webdriver.Remote(command_executor=url, options=options)


def get_test_configurations() -> List[Dict]:
    """Define 5 different browser/OS combinations for parallel testing."""
    return [
        {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "os": "Windows",
            "osVersion": "11",
            "sessionName": "El Pais Scraper - Chrome Windows 11",
            "buildName": "El Pais Opinion Scraper Build",
            "projectName": "El Pais Web Scraping",
        },
        {
            "browserName": "Firefox",
            "browserVersion": "latest",
            "os": "Windows",
            "osVersion": "10",
            "sessionName": "El Pais Scraper - Firefox Windows 10",
            "buildName": "El Pais Opinion Scraper Build",
            "projectName": "El Pais Web Scraping",
        },
        {
            "browserName": "Safari",
            "browserVersion": "latest",
            "os": "OS X",
            "osVersion": "Ventura",
            "sessionName": "El Pais Scraper - Safari Mac",
            "buildName": "El Pais Opinion Scraper Build",
            "projectName": "El Pais Web Scraping",
        },
        {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "deviceName": "Samsung Galaxy S23",
            "osVersion": "13.0",
            "sessionName": "El Pais Scraper - Chrome Android",
            "buildName": "El Pais Opinion Scraper Build",
            "projectName": "El Pais Web Scraping",
            "realMobile": "true",
        },
        {
            "browserName": "Safari",
            "browserVersion": "latest",
            "deviceName": "iPhone 14",
            "osVersion": "16",
            "sessionName": "El Pais Scraper - Safari iPhone",
            "buildName": "El Pais Opinion Scraper Build",
            "projectName": "El Pais Web Scraping",
            "realMobile": "true",
        },
    ]


def run_test_on_browser(config: dict, test_id: int) -> dict:
    """Run the scraping test on a specific browser configuration."""
    print(f"\n[Test {test_id}] Starting: {config['sessionName']}")
    driver = None
    
    try:
        driver = get_browserstack_driver(config)
        print(f"[Test {test_id}] Driver created successfully")
        
        # Run the scraping
        scraped = scrape_first_n_opinion_articles(driver, n=5)
        titles_es = [r["title_es"] for r in scraped]
        
        # Translate
        translated = translate_many(titles_es, from_lang="es", to_lang="en")
        
        # Analyze
        analysis = analyze_translated_headers(translated)
        
        print(f"[Test {test_id}] ✅ SUCCESS: {config['sessionName']}")
        print(f"[Test {test_id}] Scraped {len(scraped)} articles")
        print(f"[Test {test_id}] Repeated words: {analysis['repeated_more_than_two']}")
        
        # Mark test as passed in BrowserStack
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test completed successfully"}}'
        )
        
        return {
            "config": config["sessionName"],
            "status": "PASSED",
            "articles_count": len(scraped),
            "repeated_words": analysis["repeated_more_than_two"],
        }
        
    except Exception as e:
        print(f"[Test {test_id}] ❌ FAILED: {config['sessionName']}")
        print(f"[Test {test_id}] Error: {str(e)}")
        
        if driver:
            try:
                driver.execute_script(
                    f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"failed", "reason": "{str(e)[:100]}"}}}}'
                )
            except Exception:
                pass  # Ignore if script execution fails
        
        return {
            "config": config["sessionName"],
            "status": "FAILED",
            "error": str(e),
        }
        
    finally:
        if driver:
            try:
                driver.quit()
                print(f"[Test {test_id}] Driver closed")
            except Exception:
                pass


def run_parallel_tests():
    """Run tests in parallel across 5 browser configurations."""
    configs = get_test_configurations()
    results = []
    
    print("=" * 80)
    print("Starting BrowserStack Parallel Tests (5 threads)")
    print("=" * 80)
    
    # Run tests in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(run_test_on_browser, config, i + 1): config
            for i, config in enumerate(configs)
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    for i, result in enumerate(results, 1):
        status_symbol = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{i}. {status_symbol} {result['config']}: {result['status']}")
        if result["status"] == "PASSED":
            print(f"   Articles: {result['articles_count']}, Repeated words: {result['repeated_words']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 80)
    
    # Print BrowserStack dashboard link
    print("\n📊 View results on BrowserStack Dashboard:")
    print("   https://automate.browserstack.com/dashboard/v2")
    print("\n")
    
    return results


if __name__ == "__main__":
    run_parallel_tests()