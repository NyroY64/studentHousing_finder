import requests
import json
from bs4 import BeautifulSoup
import re
import logging
import sqlite3
import smtplib
import os
from email.message import EmailMessage
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.config import BASE_URL, DEPARTMENTS

class Scraper:
    def __init__(self):
        self.configure_logging()
        # Use data directory for database
        db_path = Path(__file__).parent.parent.parent / 'data' / 'residences.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_conn = sqlite3.connect(str(db_path))
        self.create_database_table()

    def create_database_table(self):
        """Ensures the residences table exists in the database."""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS residences (
                id TEXT PRIMARY KEY,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_conn.commit()

    def is_new_residence(self, residence_id):
        """Checks if a residence ID is already in the database."""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id FROM residences WHERE id = ?", (residence_id,))
        return cursor.fetchone() is None

    def add_residence_to_db(self, residence_id):
        """Adds a new residence ID to the database."""
        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO residences (id) VALUES (?)", (residence_id,))
        self.db_conn.commit()
        logging.info(f"Added new residence {residence_id} to the database.")

    def send_email_notification(self, new_residences):
        """Sends an email notification with the list of new residences."""
        email_address = os.environ.get('EMAIL_ADDRESS')
        email_password = os.environ.get('EMAIL_PASSWORD')
        recipient_address = os.environ.get('RECIPIENT_ADDRESS', email_address)

        if not all([email_address, email_password, recipient_address]):
            logging.error("Email credentials or recipient not set. Skipping email notification.")
            return

        msg = EmailMessage()
        msg['Subject'] = f"🏠 New Housing Alert: {len(new_residences)} New Residences Found!"
        msg['From'] = email_address
        msg['To'] = recipient_address

        body = "🎉 Great news! The following new residences are now available:\n\n"
        body += "=" * 70 + "\n\n"
        
        for i, res in enumerate(new_residences, 1):
            body += f"#{i} - {res['title']}\n"
            body += f"📍 Location: {res['address']}, {res['city']} ({res['postal_code']})\n"
            
            # Add contact info if available
            if res.get('phone'):
                body += f"📞 Phone: {res['phone']}\n"
            if res.get('email'):
                body += f"📧 Email: {res['email']}\n"
            
            body += f"🔗 Book now: {res['link']}\n"
            body += "\n" + "-" * 70 + "\n\n"
        
        body += "\n⚡ Act fast! Student housing goes quickly.\n"
        body += "💡 Tip: Contact them directly by phone for faster response.\n"
        
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_address, email_password)
                smtp.send_message(msg)
            logging.info("Successfully sent email notification.")
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")

    def configure_logging(self):
        """Configures the logging for the application."""
        # Use DEBUG level for more verbose output
        log_level = logging.DEBUG if os.environ.get('DEBUG') else logging.INFO
        
        # Use logs directory
        log_path = Path(__file__).parent.parent.parent / 'logs' / 'scraper.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=str(log_path),
            filemode='w'
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if not logging.getLogger().hasHandlers():
            logging.getLogger().addHandler(console_handler)

    def fetch_residences(self):
        """Fetches residence data from the Fac Habitat API."""
        url = f"{BASE_URL}/fr/residences/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info("Successfully fetched main residence data from the API.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from API: {e}")
            return None

    def filter_residences_by_department(self, residences, departments):
        """Filters residences based on a list of desired department codes."""
        filtered_residences = {}
        for residence_id, residence_data in residences.items():
            cp = residence_data.get('cp', '')
            if cp and len(cp) >= 2:
                postal_code_prefix = cp[:2]
                if postal_code_prefix in departments:
                    filtered_residences[residence_id] = residence_data
        logging.info(f"Found {len(filtered_residences)} residences in desired departments.")
        return filtered_residences

    def check_residence_availability(self, residence_url):
        """Checks the availability of a single residence by scraping its page and iframe."""
        try:
            response = requests.get(residence_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            iframe = soup.find('iframe', {'class': 'reservation'})
            if iframe and 'src' in iframe.attrs:
                iframe_url = iframe['src']
                if not iframe_url.startswith('http'):
                    iframe_url = f"{BASE_URL}{iframe_url}"
                
                # DEBUG: Log iframe URL to help reverse engineer the pattern
                logging.debug(f"Iframe URL for {residence_url}: {iframe_url}")
                
                iframe_response = requests.get(iframe_url, timeout=10)
                iframe_response.raise_for_status()
                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                
                # DEBUG: Check for any script tags that might contain JSON data
                scripts = iframe_soup.find_all('script')
                for script in scripts:
                    if script.string and ('availability' in script.string.lower() or 'disponible' in script.string.lower()):
                        logging.debug(f"Found potential availability data in script: {script.string[:200]}...")
                
                availability_span = iframe_soup.find('span', {'id': 'avail_area_0'})
                if availability_span:
                    availability_text = availability_span.text.strip()
                    logging.debug(f"Availability text: {availability_text}")
                    if "Disponible" in availability_text or "Disponibilité à venir" in availability_text:
                        logging.info(f"Availability found for {residence_url}")
                        return True
            return False
        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking availability for {residence_url}: {e}")
            return False

    def save_results(self, results):
        """Saves the list of available residences to a JSON file."""
        output_path = Path(__file__).parent.parent.parent / 'data' / 'available_residences.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logging.info(f"Successfully saved {len(results)} available residences to {output_path}")
        except IOError as e:
            logging.error(f"Failed to save results to {output_path}: {e}")

    def run(self):
        """Main execution method for the scraper."""
        all_residences = self.fetch_residences()
        if all_residences:
            filtered_residences = self.filter_residences_by_department(all_residences, DEPARTMENTS)
            newly_available_residences = []
            for residence_id, residence_data in filtered_residences.items():
                slugified_title = residence_data['titre_fr'].replace(' ', '-').lower()
                residence_link = f"{BASE_URL}/fr/residences-etudiantes/id-{residence_id}-{slugified_title}"
                if "logifac.fr" in residence_link.lower() or residence_data.get('gestionnaire', '').lower() == 'loch':
                    logging.info(f"Ignoring Logifac residence: {residence_data['titre_fr']}")
                    continue
                logging.info(f"Checking availability for {residence_data['titre_fr']} (ID: {residence_id})...")
                if self.check_residence_availability(residence_link):
                    if self.is_new_residence(residence_id):
                        logging.info(f"Found new available residence: {residence_data['titre_fr']}")
                        self.add_residence_to_db(residence_id)
                        newly_available_residences.append({
                            'id': residence_id,
                            'title': residence_data['titre_fr'],
                            'address': residence_data['adresse'],
                            'city': residence_data['ville'],
                            'postal_code': residence_data.get('cp', 'N/A'),
                            'phone': residence_data.get('tel', None),
                            'email': residence_data.get('email', None),
                            'link': residence_link
                        })
                    else:
                        logging.info(f"Residence {residence_id} is already known.")

            if newly_available_residences:
                self.save_results(newly_available_residences)
                self.send_email_notification(newly_available_residences)
                logging.info(f"Found {len(newly_available_residences)} new residences.")
            else:
                logging.info("No new available residences found.")
        
        self.db_conn.close()

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
