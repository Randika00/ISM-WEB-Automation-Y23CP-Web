import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_BR_N_TXLR RULES'
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

def rule_check_pdf(rule_name, pdf_content, file_name, location_id):
    cleaned_rule_name = common_module.clean_rule_title(rule_name)
    cleaned_rule_title_new = re.sub(r'\s+', ' ', rule_name.replace('"', '').strip())
    cleaned_rule_title_new = common_module.shorten_rule_name(cleaned_rule_title_new)

    if not cleaned_rule_name in ignore_rules and len(cleaned_rule_name) > 0:
        if not cleaned_rule_name in allowed_rules:
            common_module.append_new_rule(source_id, cleaned_rule_title_new)

        output_file_name = common_module.ret_file_name_full(source_id, location_id, file_name, '.pdf')
        with open(output_file_name, 'wb') as file:
            file.write(pdf_content)
            print(f"Downloaded: {output_file_name}")

def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

def scrape_and_download(sheet_links, location_id):
    for category, url in sheet_links.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")

        tr_elements = soup.find_all('tr')

        for tr_element in tr_elements:
            links = tr_element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if 'https://www.txnb.uscourts.gov/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = link.get_text(strip=True)
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, location_id)
                    else:
                        print(f"Failed to download: {pdf_url}")

        div_content = soup.find('div', class_='view-content')
        if div_content:
            links = div_content.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if '/sites/txnb/files/local_rules/' in href:
                    pdf_url = urllib.parse.urljoin(url, href)
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        pdf_name = "Local Rules of Bankruptcy"
                        output_file_name = format_pdf_name(pdf_name)
                        rule_check_pdf(pdf_name, response.content, output_file_name, location_id)
                    else:
                        print(f"Failed to download: {pdf_url}")

if __name__ == "__main__":
    sheet_links_general = {
        'Northern District of Texas General Orders - 01': 'https://www.txnb.uscourts.gov/court-info/general-orders',
        'Northern District of Texas General Orders - 02': 'https://www.txnb.uscourts.gov/court-info/general-orders?page=1',
        'Northern District of Texas General Orders - 03': 'https://www.txnb.uscourts.gov/court-info/general-orders?page=2',
        'Northern District of Texas General Orders - 04': 'https://www.txnb.uscourts.gov/court-info/general-orders?page=3',
        'Northern District of Texas General Orders - 05': 'https://www.txnb.uscourts.gov/court-info/general-orders?page=4',
    }

    sheet_links_local = {
        'Northern District of Texas Local Bankruptcy Rules': 'https://www.txnb.uscourts.gov/court-info/local-rules-and-orders/local-rules',
    }

    # Scraping and downloading general orders
    scrape_and_download(sheet_links_general, 'General Orders')

    # Scraping and downloading local rules
    scrape_and_download(sheet_links_local, 'Local Rules')
