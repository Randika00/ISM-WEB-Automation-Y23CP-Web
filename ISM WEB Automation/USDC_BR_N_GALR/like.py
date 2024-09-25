import os
import requests
from bs4 import BeautifulSoup
import common_module
import re
import urllib.parse
from datetime import datetime

source_id = 'USDC_BR_N_GALR RULES'
location_id = 'General Orders'

allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('ignored_rules.txt')

# Sheet links containing desired URLs
sheet_links = {
    'Northern District of Georgia Local Bankruptcy Rules - 01': 'https://www.ganb.uscourts.gov/court-info/local-rules-and-orders/general-orders',
    'Northern District of Georgia Local Bankruptcy Rules - 02': 'https://www.ganb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=1',
    'Northern District of Georgia Local Bankruptcy Rules - 03': 'https://www.ganb.uscourts.gov/court-info/local-rules-and-orders/general-orders?page=2',
}

# Function to check PDF rules
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

# Function to format PDF names
def format_pdf_name(pdf_name):
    formatted_name = re.sub(r'[.;]', ' ', pdf_name)
    formatted_name = re.sub(r'(\d+)\s+', r'\1. ', formatted_name, 1)
    return f"{formatted_name.strip()}"

# Desired links for each section
desired_links_01 = [
    '/content/third-amended-and-restated-general-order-no-24-2018',
    '/content/amended-and-restated-general-order-45-2021',
    '/content/second-amended-and-restated-general-order-no-26-2019',
    '/content/amended-and-restated-general-order-37-2020',
    '/content/general-order-no-48-2022',
    '/content/general-order-no-47-2022',
    '/content/general-order-no-46-2021',
    '/content/general-order-no-44-2021',
    '/content/amended-and-restated-general-order-no-42-2020',
    '/content/amended-and-restated-general-order-no-30-2020'
]

desired_links_02 = [
    '/content/general-order-no-43-2020',
    '/content/general-order-no-41-2020',
    '/content/general-order-no-39-2020',
    '/content/general-order-no-38-2020',
    '/content/general-order-no-36-2020',
    '/content/general-order-no-32-2020',
    '/content/general-order-no-31-2020',
    '/content/general-order-no-29-2019',
    '/content/general-order-no-28-2019',
    '/content/general-order-no-27-2019'
]

desired_links_03 = [
    '/content/general-order-no-25-2018',
    '/content/general-order-no-20-2016',
    '/content/general-order-9-2008',
    '/content/general-order-5-2006',
    '/content/general-order-2-2005'
]

today_date = datetime.today().strftime('%Y%m%d')

base_path = f"out/USDC_BR_N_GALR RULES/{today_date}/"
location_path = os.path.join(base_path, location_id)

if not os.path.exists(location_path):
    os.makedirs(location_path)

# Combine all desired links
all_desired_links = {
    'Northern District of Georgia Local Bankruptcy Rules - 01': desired_links_01,
    'Northern District of Georgia Local Bankruptcy Rules - 02': desired_links_02,
    'Northern District of Georgia Local Bankruptcy Rules - 03': desired_links_03,
}

# Iterate through each section in sheet_links
for category, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    ul_elements = soup.find_all('ul')

    # Get corresponding desired links based on the category
    desired_links = all_desired_links.get(category, [])

    for ul_element in ul_elements:
        links = ul_element.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href in desired_links:
                content_url = 'https://www.ganb.uscourts.gov' + href
                print(f"Processing content link: {content_url}")

                content_response = requests.get(content_url)
                if content_response.status_code == 200:
                    content_soup = BeautifulSoup(content_response.text, "html.parser")

                    # Identify and download PDFs
                    pdf_links = content_soup.find_all('a', href=re.compile(r'\.pdf$'))
                    for pdf_link in pdf_links:
                        pdf_url = urllib.parse.urljoin(content_url, pdf_link.get('href'))
                        pdf_name = pdf_link.get_text()

                        # Check if the link ends with ".pdf"
                        if pdf_url.endswith('.pdf'):
                            print(f"Found PDF: {pdf_url}")

                            pdf_response = requests.get(pdf_url)
                            if pdf_response.status_code == 200:
                                # Save the PDF file to the specified location
                                pdf_path = os.path.join(location_path, pdf_name)
                                with open(pdf_path, 'wb') as pdf_file:
                                    pdf_file.write(pdf_response.content)
                                    print(f"Downloaded: {pdf_name} at {pdf_path}")
                            else:
                                print(f"Failed to download PDF from: {pdf_url}")
                        else:
                            print(f"Skipping non-PDF document: {pdf_url}")
