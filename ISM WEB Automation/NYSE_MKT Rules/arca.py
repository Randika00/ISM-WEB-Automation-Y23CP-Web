import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

source_id = 'NYSE_MKT Rules'

# Load the list of allowed rules from a file
allowed_rules = []
try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'allow_rules.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

sheet_links = {
    'NYSE ARCA RULES - Options Rules': "https://nysearcaguide.srorules.com/rules",
    'NYSE ARCA RULES - Equity Rules': "https://nysearcaguide.srorules.com/rules"
}

for rule_name, url in sheet_links.items():
    resource = requests.get(url, headers=headers)
    soup = BeautifulSoup(resource.text, "html.parser")

# Define functions for file and folder names

def ret_file_name_full(source_id, location_id, rule_name, extension):
    exe_folder = os.path.dirname(os.path.abspath(__file__))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    index = 1
    outFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + extension)
    retFileName = outFileName
    while os.path.isfile(retFileName):
        retFileName = os.path.join(out_path, remove_invalid_paths(rule_name) + "_" + str(index) + extension)
        index += 1
    return retFileName

def ret_out_folder(source_id, location_id):
    exe_folder = os.path.dirname(os.path.abspath(__file__))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules', remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)

# Find the section and li elements
section = soup.find('div', class_="cg-card-container-1-10-0")

if section:
    ul_element = section.find('ul')
    if ul_element:
        li_elements = ul_element.find_all('li')
        for li in li_elements:
            link = li.find('a', href=True)
            if link:
                rule_url = 'https://nysearcaguide.srorules.com/rules/' + link['href']
                filename = os.path.basename(rule_url)
                if filename.endswith('.docx'):
                    rule_response = requests.get(rule_url)
                    if rule_response.status_code == 200:
                        full_path = ret_file_name_full(source_id, 'NYSE ARCA RULES', filename, '.docx')
                        with open(full_path, 'wb') as f:
                            f.write(rule_response.content)
                        print(f"Downloaded: {filename}")
                    else:
                        print(f"Failed to download: {filename}")
    else:
        print("UL element not found")
else:
    print("Section not found")

