import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse

source_id = 'USDC_C_ILLR RULES'
location_id = 'New Rules'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

sheet_links = {
    'Central District of Illinois Local Rules': 'https://www.ilcd.uscourts.gov/local-rules',
}


def rule_check_pdf(rule_name, pdf_content, file_name):
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


def format_pdf_name(name1, name2):
    return f"{name1.strip()}. {name2.strip()}"


for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    tr_elements = soup.find_all('tr')

    for tr_element in tr_elements:
        try:
            tds = tr_element.find_all('td', class_='rtecenter')
            if len(tds) >= 2:
                pdf_name = format_pdf_name(tds[0].get_text(strip=True), tds[1].get_text(strip=True))
                links = tr_element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/sites/ilcd/files/' in href:
                        pdf_url = urllib.parse.urljoin(url, href)
                        print(f"Downloading: {pdf_url}")
                        response = requests.get(pdf_url)
                        if response.status_code == 200:
                            output_file_name = format_pdf_name(tds[0].get_text(strip=True), tds[1].get_text(strip=True))
                            rule_check_pdf(pdf_name, response.content, output_file_name)
                        else:
                            print(f"Failed to download: {pdf_url} - Status Code: {response.status_code}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
