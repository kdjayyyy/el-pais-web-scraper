# El País Opinion Section Web Scraper

Automated web scraping solution for El País Spanish news outlet, with translation and text analysis capabilities.

## 🌟 Features

- 🌐 **Web Scraping**: Scrapes articles from El País Opinion section
- 🇪🇸 **Spanish Content**: Ensures content is displayed in Spanish
- 🖼️ **Image Download**: Automatically downloads article cover images
- 🔤 **Translation**: Translates Spanish article titles to English using RapidAPI
- 📊 **Text Analysis**: Analyzes translated text for repeated words (>2 occurrences)
- 🧪 **Cross-Browser Testing**: Runs on BrowserStack across 5 parallel threads
- 💻 **Multiple Platforms**: Tests on desktop (Windows, macOS) and mobile (Android, iOS)

## 🛠️ Technologies

- **Python 3.12**
- **Selenium WebDriver** - Browser automation
- **BrowserStack Automate** - Cloud testing platform
- **RapidAPI Translate** - Translation service
- **ThreadPoolExecutor** - Parallel test execution
- **WebDriverManager** - Automatic ChromeDriver management

## 📁 Project Structure

```
Scraper/
├── src/
│   ├── __init__.py
│   ├── elpais_scraper.py      # Main scraping logic
│   ├── browserstack_runner.py # BrowserStack parallel execution
│   ├── translator.py           # Translation API integration
│   └── utils.py                # Helper functions (image download, tokenization)
├── tests/
│   └── test_el_pais.py         # Unit tests
├── images/                     # Downloaded article cover images
├── .vscode/
│   └── settings.json           # VS Code workspace settings
├── .env                        # Environment variables (not committed)
├── .gitignore                  # Git ignore rules
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.12 or higher
- Git
- Chrome browser (for local testing)

### 1. Clone the Repository

```bash
git clone https://github.com/kdjayyyy/el-pais-web-scraper.git
cd el-pais-web-scraper
```

### 2. Create Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
python -m venv venv
.\venv\Scripts\activate
```

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# RapidAPI Translation
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=rapid-translate-multi-traduction.p.rapidapi.com

# BrowserStack Credentials
BROWSERSTACK_USERNAME=your_browserstack_username
BROWSERSTACK_ACCESS_KEY=your_browserstack_access_key

# Optional: Run in headless mode (true/false)
HEADLESS=true
```

#### Getting API Keys:

**RapidAPI:**
1. Sign up at https://rapidapi.com/
2. Subscribe to "Rapid Translate Multi Traduction API"
3. Copy your API key from the dashboard

**BrowserStack:**
1. Sign up for free trial at https://www.browserstack.com/automate
2. Go to Settings → Automate
3. Copy your Username and Access Key

## 📖 Usage

### Run Locally (Single Browser)

Scrape articles and test locally using Chrome:

```bash
python -m src.elpais_scraper
```

### Run on BrowserStack (5 Parallel Browsers)

Execute tests across multiple browsers simultaneously:

```bash
python -m src.browserstack_runner
```

**This will test on:**
1. ✅ Chrome on Windows 11
2. ✅ Firefox on Windows 10
3. ✅ Safari on macOS Ventura
4. ✅ Chrome on Samsung Galaxy S23 (Android 13)
5. ✅ Safari on iPhone 14 (iOS 16)

### Run Unit Tests

```bash
# Using pytest
pytest tests/

# Using unittest
python -m unittest tests.test_el_pais

# Run with verbose output
pytest tests/ -v
```

## 🔧 Configuration

### Headless Mode

To run Chrome in headless mode (no browser UI), set in `.env`:
```env
HEADLESS=true
```

To see the browser (useful for debugging):
```env
HEADLESS=false
```

### VS Code Python Environment

The project includes VS Code settings to automatically use environment variables from `.env` in integrated terminals. Make sure you have:
- Python extension installed
- `python.terminal.useEnvFile` enabled (already configured in `.vscode/settings.json`)

## 📊 BrowserStack Results

**Public Build Link:** [View on BrowserStack](https://automate.browserstack.com/projects/El%20Pais%20Web%20Scraping/builds/El+Pais+Opinion+Scraper+Build/2?tab=tests&testListView=flat&public_token=559c5359542856babfd365bcdcca430b9765937d1583e883486dc97dad4588e4)

**Test Run Screenshot:** [Google Drive Link](https://drive.google.com/file/d/1TUUS7nEZfcMAqaBnytDSbGgivh6mvcOz/view?usp=sharing)

### Build Information
- **Build Name:** El Pais Opinion Scraper Build
- **Project:** El Pais Web Scraping
- **Parallel Sessions:** 5
- **Execution Time:** ~2-3 minutes


## 🧪 How It Works

### 1. Article Discovery
```python
# Navigate to Opinion homepage
opinion_url = "https://elpais.com/opinion/"

# Find article links using CSS selectors
anchors = driver.find_elements(By.CSS_SELECTOR, "article h2 a, article h3 a")

# Filter for actual articles (with dates in URL)
# Skip section pages like /opinion/editoriales/
```

### 2. Title Extraction (Multi-Fallback Strategy)
```python
# Strategy 1: Capture from homepage (before navigation)
homepage_title = anchor.text.strip()

# Strategy 2: Try h1 on article page
title = driver.find_element(By.TAG_NAME, "h1").text

# Strategy 3: Fallback to homepage title if h1 empty
if not title:
    title = homepage_title

# Strategy 4: Last resort - og:title meta tag
meta = driver.find_element(By.XPATH, "//meta[@property='og:title']")
title = meta.get_attribute("content")
```

### 3. Translation with Retry Logic
```python
# Retry up to 3 times if rate limited
for attempt in range(3):
    if resp.status_code == 429:  # Rate limit
        wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
        time.sleep(wait_time)
        continue
```

### 4. Word Analysis
```python
# Normalize: lowercase, remove punctuation
# Tokenize: split into words
# Count: use Counter to find frequencies
# Filter: words appearing > 2 times
```

## 🐛 Troubleshooting

### Common Issues

**1. "ChromeDriver not found" error:**
```bash
# The script auto-downloads ChromeDriver, but if it fails:
# Install manually or ensure Chrome is installed
```

**2. "Translation failed - 429 Rate Limit":**
```
# RapidAPI free tier has limited requests
# Solution: Wait a few minutes or upgrade plan
# Fallback: Original Spanish text is used
```

**3. "BrowserStack credentials not found":**
```bash
# Ensure .env file exists and has correct credentials
# Check: echo $BROWSERSTACK_USERNAME (Linux/Mac)
# Check: echo %BROWSERSTACK_USERNAME% (Windows)
```

**4. "Empty titles for some articles":**
```
# This is handled by fallback logic
# The scraper tries multiple methods to extract titles
# If all fail, checks og:title meta tag
```

**5. "Selenium 'desired_capabilities' error":**
```bash
# Update to Selenium 4.x compatible code
# Use browser-specific Options classes instead
pip install --upgrade selenium
```

## 📦 Dependencies

```txt
selenium>=4.15.0
webdriver-manager>=4.0.1
requests>=2.31.0
python-dotenv>=1.0.0
```

Install all at once:
```bash
pip install -r requirements.txt
```
