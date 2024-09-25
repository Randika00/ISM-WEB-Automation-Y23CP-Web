import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

import PyPDF2
import pandas as pd

source_id='Illinois State Court Rules'
# url ="https://www.illinoiscourts.gov/courts/supreme-court/courts-supreme-court-illinois-rules-of-evidence/"

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


allow_rules=[]
try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'links.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]



sheet_links = {
                'Rules of Evidence': 'https://www.illinoiscourts.gov/courts/supreme-court/courts-supreme-court-illinois-rules-of-evidence/',
                'Judicial Circuit Rules - 3rd Judicial Circuit Rules':  'https://www.madisoncountyil.gov/departments/circuit_court/about/local_rules_and_pro_hac_vice_information.php',
                'Judicial Circuit Rules - 6th Judicial Circuit Rules':  'https://www.sixthcircuitcourt.com/localrules.php',
                'Judicial Circuit Rules - 7th Judicial Circuit Rules':  'https://co.sangamon.il.us/departments/s-z/seventh-judicial-circuit-court/seventh-circuit-court-rules-of-practice',
                'Judicial Circuit Rules - 10th Judicial Circuit Rules':  'https://www.10thcircuitcourtil.org/297/Circuit-Court-Rules',
                'Judicial Circuit Rules - 14th Judicial Circuit Rules':  'https://www.rockislandcountyil.gov/165/Local-Court-Rules-Forms',
                'Judicial Circuit Rules - 16th Judicial Circuit Rules':  'https://www.illinois16thjudicialcircuit.org/Pages/localCourtRules.aspx',

               }
for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")
    print(resource.status_code)

    # print(soup)

    pdf_folder = 'pdf'
    os.makedirs(pdf_folder, exist_ok=True)
    error_dict = {}
    error_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    links = soup.find("table", {"id": "ctl04_gvRules"}).findAll('tr')
    for i in links:
        if i.find('a'):
            labelTd = str(i.findAll('td')[1].get_text()).strip()
            text2 = i.find('a').text.strip().replace('â€ƒ', ' ').replace('â€‰', ' ')
            combined_text = (labelTd + ". " + text2).replace('\n', ' ').strip()
            print(combined_text)
            pdf_url = 'https://www.illinoiscourts.gov' + str(i.find('a')['href'])
            if combined_text in allowed_rules:
                response = requests.get(pdf_url, allow_redirects=False)
                head = response.headers;
                print(head)
                print(pdf_url)
                pdf_response = requests.get(pdf_url, headers=head)
                pdf_path = ret_file_name_full(source_id, rule_name, combined_text, '.pdf')
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)
                print(f"Downloaded: {pdf_path}")















