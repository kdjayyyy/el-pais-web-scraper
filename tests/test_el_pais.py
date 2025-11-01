import unittest
from unittest.mock import Mock, patch
from src.elpais_scraper import (
    scrape_first_n_opinion_articles,
    analyze_translated_headers,
)
from src.utils import normalize_and_tokenize

class TestElPaisScraper(unittest.TestCase):
    """Unit tests for El País scraper functionality."""

    def test_normalize_and_tokenize(self):
        """Test text normalization and tokenization."""
        text = "Brazil, violence of crime"
        tokens = normalize_and_tokenize(text)
        self.assertIn("brazil", tokens)
        self.assertIn("violence", tokens)
        self.assertIn("of", tokens)
        self.assertIn("crime", tokens)

    def test_analyze_translated_headers_finds_repeats(self):
        """Test that repeated words are correctly identified."""
        headers = [
            "The triumph of secularism",
            "The violence of crime",
            "The nature of celebration",
        ]
        result = analyze_translated_headers(headers)
        
        # 'the' appears 3 times, 'of' appears 3 times
        self.assertIn("the", result["repeated_more_than_two"])
        self.assertIn("of", result["repeated_more_than_two"])
        self.assertEqual(result["repeated_more_than_two"]["the"], 3)
        self.assertEqual(result["repeated_more_than_two"]["of"], 3)

    def test_analyze_translated_headers_no_repeats(self):
        """Test with no repeated words."""
        headers = ["One unique title", "Another different header"]
        result = analyze_translated_headers(headers)
        
        # No words repeated more than twice
        self.assertEqual(len(result["repeated_more_than_two"]), 0)

    def test_analyze_translated_headers_empty_input(self):
        """Test with empty headers."""
        headers = []
        result = analyze_translated_headers(headers)
        
        self.assertEqual(len(result["repeated_more_than_two"]), 0)
        self.assertEqual(len(result["counts"]), 0)


if __name__ == "__main__":
    unittest.main()