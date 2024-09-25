import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys


source_id='Illinois State Court Rules'

allow_rules=[]
try:
    with open('allow_rules.txt', 'r', encoding='utf-8') as my_file:
        allowed_rules = my_file.readlines()
except FileNotFoundError:
    print("File 'links.txt' not found. Please make sure it exists.")
allowed_rules = [rule.strip().replace('â€ƒ', ' ').replace('â€‰', ' ') for rule in allowed_rules]


sheet_links = {
               'Judicial Circuit Rules - 3rd Judicial Circuit Rules': 'https://www.madisoncountyil.gov/departments/circuit_court/about/local_rules_and_pro_hac_vice_information.php',
               'Judicial Circuit Rules - 6th Judicial Circuit Rules':  'https://www.sixthcircuitcourt.com/localrules.php',
               'Judicial Circuit Rules - 7th Judicial Circuit Rules':  'https://co.sangamon.il.us/departments/s-z/seventh-judicial-circuit-court/seventh-circuit-court-rules-of-practice',
               'Judicial Circuit Rules - 10th Judicial Circuit Rules':  'https://www.10thcircuitcourtil.org/297/Circuit-Court-Rules',
               'Judicial Circuit Rules - 18th Judicial Circuit Rules':  'https://www.dupagecourts.gov/18th_judicial_circuit_court/legal_resources/court_rules/',
               'Judicial Circuit Rules - 22nd Judicial Circuit Rules':  'https://www.mchenrycountyil.gov/county-government/courts/22nd-judicial-circuit/local-court-rules'
              }
for rule_name, url in sheet_links.items():
    resource = requests.get(url)
    soup = BeautifulSoup(resource.text, "html.parser")
    #print(resource.status_code)

# print(soup)

pdf_folder = 'pdf'
os.makedirs(pdf_folder, exist_ok=True)
error_dict = {}
error_list = []
headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}



def ret_file_name_full(source_id, location_id, rule_name, extention):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y%m%d")
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), remove_invalid_paths(location_id),(date_prefix))
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
    out_path = os.path.join(exe_folder, 'out', remove_invalid_paths(source_id), 'Skip Rules', remove_invalid_paths(location_id), date_prefix)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    return out_path

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|]', "", path_val)


section = soup.find('article',class_ = "post clearfix")

p_element = section.findAll('p')
ul_element = section.findAll('ul')

p_element.extend(ul_element)



for i in p_element:
    pdf_url = ('https://cms4files.revize.com/madisoncountyilus/' + i.find('a')['href'])
    if i.text.strip() in allowed_rules:
        response = requests.head(pdf_url, allow_redirects=False)
        head = response.headers
        print(head)
        print(pdf_url)
        pdf_response = requests.get(pdf_url, headers=head)
        rule_name = i.text.strip()
        pdf_path = ret_file_name_full(source_id, rule_name, '.pdf')
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {pdf_path}")








