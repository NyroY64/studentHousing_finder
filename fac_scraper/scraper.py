import requests
from bs4 import BeautifulSoup
import json
import logging
from fac_scraper.utils import clean_url
from fac_scraper.config import BASE_URL, DEPARTMENTS

class Scraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            filename="data/logs/scraper.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def fetch(self, url):
        """Fetch the content of a URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching URL: {url}, Error: {e}")
            return None

    def parse_residences(self, response):
        """Extract residence addresses and links."""
        soup = BeautifulSoup(response.content, "lxml")
        deck = soup.find('ul', {'class': 'block-grid large-block-grid-2 small-block-grid-1'})
        if not deck:
            self.logger.warning("No residences found on the page.")
            return []

        residences = []
        for card in deck.contents:
            if not isinstance(card, str):
                link_tag = card.find('a', class_='visuel-liste')
                address_tag = card.find('div', class_='liste-residence-adresse')

                link = clean_url(link_tag['href']) if link_tag and 'href' in link_tag.attrs else None
                address = address_tag.text.strip() if address_tag else None

                if link and address:
                    residences.append({"address": address, "link": link})
        return residences

    def filter_residences(self, residences):
        """Filter residences based on department codes."""
        filtered = []
        for residence in residences:
            try:
                postal_code = residence['address'].split('-')[1].strip().split()[0][:2]
                if postal_code in DEPARTMENTS:
                    filtered.append(residence)
            except IndexError:
                self.logger.warning(f"Failed to extract postal code: {residence}")
        return filtered

    def check_availability(self, residences):
        """Check availability of residences."""
        available_residences = []
        for residence in residences:
            if "logifac.fr" in residence['link']:
                self.logger.info(f"Ignoring Logifac residence: {residence['address']}")
                continue

            response = self.fetch(residence['link'])
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            iframe = soup.find('iframe', {'class': 'reservation'})
            if iframe and 'src' in iframe.attrs:
                iframe_response = self.fetch(iframe['src'])
                if not iframe_response:
                    continue

                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                availability_span = iframe_soup.find('span', {'id': 'avail_area_0'})
                if availability_span:
                    availability_text = availability_span.text.strip()
                    if "Disponible" in availability_text or "Disponibilité à venir" in availability_text:
                        available_residences.append(residence)
        return available_residences

    def save_results(self, results, output_file="data/residences.json"):
        """Save the results to a JSON file."""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Results saved to {output_file}")
        except IOError as e:
            self.logger.error(f"Error saving results to file: {e}")

    def run(self):
        """Main execution method."""
        url = f"{BASE_URL}/fr/residences-etudiantes?&limit=0"
        response = self.fetch(url)
        if not response:
            return

        residences = self.parse_residences(response)
        filtered_residences = self.filter_residences(residences)
        available_residences = self.check_availability(filtered_residences)
        self.save_results(available_residences)
