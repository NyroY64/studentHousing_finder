import unittest
from fac_scraper.utils import clean_url

class TestUtils(unittest.TestCase):
    def test_clean_url_relative(self):
        """Test clean_url with a relative URL."""
        relative_url = "/fr/residences-etudiantes/id-101-marne"
        expected_url = "https://www.fac-habitat.com/fr/residences-etudiantes/id-101-marne"
        self.assertEqual(clean_url(relative_url), expected_url)

    def test_clean_url_absolute(self):
        """Test clean_url with an absolute URL."""
        absolute_url = "https://www.fac-habitat.com/fr/residences-etudiantes/id-101-marne"
        self.assertEqual(clean_url(absolute_url), absolute_url)

    def test_clean_url_invalid(self):
        """Test clean_url with a completely invalid URL."""
        invalid_url = "ftp://invalid-url"
        self.assertEqual(clean_url(invalid_url), "https://www.fac-habitat.comftp://invalid-url")
