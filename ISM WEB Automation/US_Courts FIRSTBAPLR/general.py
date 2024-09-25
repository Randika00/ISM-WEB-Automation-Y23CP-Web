import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

source_id = 'US_Courts_FIRSTBAPLR'
location_id = 'General Orders'

def ret_file_name_full(source_id, location_id, rule_name, extension):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), remove_invalid_paths(location_id),
                            (date_prefix))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    out_file_name = os.path.join(out_path, remove_invalid_paths(rule_name) + extension)
    ret_file_name = out_file_name
    while os.path.isfile(ret_file_name):
        ret_file_name = os.path.join(out_path, remove_invalid_paths(rule_name) + "_" + str(index) + extension)
        index += 1
    return ret_file_name

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
     'General Orders': 'https://www.bap1.uscourts.gov/general-orders'
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

    table_content = soup.find('table')
    table = table_content.findAll('tr')
    for item in table:
        td_element = item.findAll('td')
        for i in td_element:
            anchor_tag = i.find('a')
            if anchor_tag:
                rule_url = 'https://www.bap1.uscourts.gov/' + anchor_tag.get('href')
                try:
                    pdf_response = requests.get(rule_url, headers=headers)
                    if pdf_response.status_code == 200:
                        # Extracting the text from the <a> tag for renaming
                        anchor_text = anchor_tag.get_text(strip=True)
                        title = remove_invalid_paths(anchor_text)

                        output_file_name = ret_file_name_full(source_id, location_id, title, '.pdf')

                        with open(output_file_name, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)
                        print(f"Downloaded: {output_file_name}")
                    else:
                        print(f"Failed to download: {rule_url}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading PDF from {rule_url}: {e}")
