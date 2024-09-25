import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

source_id = 'US_Courts_FIRSTBAPLR'
location_id = 'Practice and Procedure'

def ret_file_name_full(source_id, location_id, rule_name, extention):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), remove_invalid_paths(location_id),
                            (date_prefix))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + extention)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + "_" + str(index) + extention)
    index += 1
    return retFileName

def ret_out_folder(source_id, location_id):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules',
                            remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path


def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)
allow_rules = []

try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'allow_rules.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]

sheet_links = {
    'Practice and Procedure Rules': 'https://www.uscourts.gov/rules-policies/current-rules-practice-procedure'
}


for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")

    pdf_folder = 'out'
    os.makedirs(pdf_folder, exist_ok=True)
    error_dict = {}
    error_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    div_element = soup.find('div', class_='field field-name-body')
    h2_elements = div_element.find_all('h2')

    for h2 in h2_elements:
        rule_name = h2.text.strip()
        pdf_urls = []
        p_content = h2.find_next('p')

        link = p_content.find('a', href=True)
        if link:
            pdf_url = link['href']
            if not pdf_url.startswith(('http://', 'https://')):
                pdf_url = 'https://www.uscourts.gov/' + pdf_url
            pdf_urls.append(pdf_url)

        for index, pdf_url in enumerate(pdf_urls, start=1):
            try:
                pdf_response = requests.get(pdf_url)
                if pdf_response.status_code == 200:
                    output_fileName = ret_file_name_full(source_id, location_id, rule_name, f'_{index}.pdf')
                    with open(output_fileName, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                    print(f"Downloaded: {output_fileName}")
                else:
                    print(f"Failed to download: {pdf_url}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading PDF from {pdf_url}: {e}")