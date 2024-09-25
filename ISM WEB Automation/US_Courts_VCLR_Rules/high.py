import requests
import re
from bs4 import BeautifulSoup
import common_module

# Section 1: Rules of Admission and Practice
source_id_1 = 'US_Courts_VCLR_Rules'
location_id_1 = 'Rules of Admission and Practice'

allowed_rules_1 = common_module.return_lists('links.txt')
ignore_rules_1 = common_module.return_lists('ignored_rules.txt')

def process_rules_of_admission_and_practice():
    sheet_links_1 = {
        'Rules of the U.S. Court of Appeals for Veterans Claims Rules of Admission and Practice':
            'http://www.uscourts.cavc.gov/rules_of_admission_and_practice.php',
    }

    for rule_name, url in sheet_links_1.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")

        table = soup.find('table')
        table = table.findAll('tr')
        for item in table:
            td_element = item.findAll('td')
            name = ''
            for i in td_element:
                try:
                    name += str(i.text)
                    if i.find('a'):
                        rule_url = 'http://www.uscourts.cavc.gov/' + i.find('a').get('href')
                        rule_response = requests.get(rule_url, allow_redirects=False)
                        if rule_response.status_code == 200:
                            rule_html = rule_response.text
                            resource = requests.get(rule_url)
                            soup = BeautifulSoup(resource.text, "html.parser")

                            content = soup.find('div', {'id': 'content_subpage'})
                            rule_name = content.find('h1').text

                            output_fileName = common_module.ret_file_name_full(source_id_1, location_id_1, rule_name,
                                                                              '.html')
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(str(content))

                except Exception as e:
                    pass
                else:
                    print(f"Downloaded HTML for rule '{rule_name}' at URL: {rule_url}")


# Section 2: E-Filing Rules
source_id_2 = 'US_Courts_VCLR_Rules'
location_id_2 = 'E-Filing Rules'

allowed_rules_2 = common_module.return_lists('links.txt')
ignore_rules_2 = common_module.return_lists('ignored_rules.txt')

def process_e_filing_rules():
    sheet_links_2 = {
        'Rules of the U.S. Court of Appeals for Veterans Claims E-Filing Rules':
            'http://www.uscourts.cavc.gov/e_filing_rules.php'
    }

    for rule_name, url in sheet_links_2.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")

        table = soup.find('table')
        table = table.findAll('tr')
        for item in table:
            td_element = item.findAll('td')
            name = ''
            for i in td_element:
                try:
                    name += str(i.text)
                    if i.find('a'):
                        rule_url = 'http://www.uscourts.cavc.gov/' + i.find('a').get('href')
                        rule_response = requests.get(rule_url, allow_redirects=False)
                        if rule_response.status_code == 200:
                            rule_html = rule_response.text
                            resource = requests.get(rule_url)
                            soup = BeautifulSoup(resource.text, "html.parser")

                            content = soup.find('div', {'id': 'content_subpage'})
                            rule_name = content.find('h1').text

                            output_fileName = common_module.ret_file_name_full(source_id_2, location_id_2, rule_name,
                                                                              '.html')
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(str(content))

                except Exception as e:
                    pass
                else:
                    print(f"Downloaded HTML for rule '{rule_name}' at URL: {rule_url}")


# Section 3: Local Rules
source_id_3 = 'US_Courts_VCLR_Rules'
location_id_3 = 'Local Rules'

allowed_rules_3 = common_module.return_lists('links.txt')
ignore_rules_3 = common_module.return_lists('ignored_rules.txt')

def process_local_rules():
    sheet_links_3 = {
        'Rules of the U.S. Court of Appeals for Veterans Claims Local Rules':
            'http://www.uscourts.cavc.gov/rules_of_practice.php'
    }

    for rule_name, url in sheet_links_3.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")

        table = soup.find('table')
        table = table.findAll('tr')
        for item in table:
            td_element = item.findAll('td')
            name = ''
            for i in td_element:
                try:
                    name += str(i.text)
                    if i.find('a'):
                        rule_url = 'http://www.uscourts.cavc.gov/' + i.find('a').get('href')
                        rule_response = requests.get(rule_url, allow_redirects=False)
                        if rule_response.status_code == 200:
                            rule_html = rule_response.text
                            resource = requests.get(rule_url)
                            soup = BeautifulSoup(resource.text, "html.parser")

                            content = soup.find('div', {'id': 'content_subpage'})
                            rule_name = content.find('h1').text

                            output_fileName = common_module.ret_file_name_full(source_id_3, location_id_3, rule_name,
                                                                              '.html')
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(str(content))

                except Exception as e:
                    pass
                else:
                    print(f"Downloaded HTML for rule '{rule_name}' at URL: {rule_url}")


# Section 4: Veterans Claims Local Rules
source_id_4 = 'US_Courts_VCLR_Rules'
location_id_4 = 'Veterans Claims Local Rules'

allowed_rules_4 = common_module.return_lists('links.txt')
ignore_rules_4 = common_module.return_lists('ignored_rules.txt')

def process_veterans_claims_local_rules():
    sheet_links_4 = {
        'Rules of the U.S. Court of Appeals for Veterans Claims 01': 'http://www.uscourts.cavc.gov/rules_of_practice.php',
        'Rules of the U.S. Court of Appeals for Veterans Claims 02': 'http://www.uscourts.cavc.gov/rules_of_admission_and_practice.php',
        'Rules of the U.S. Court of Appeals for Veterans Claims 03': 'http://www.uscourts.cavc.gov/e_filing_rules.php',
        'Rules of the U.S. Court of Appeals for Veterans Claims Internal Operating Procedures': 'http://www.uscourts.cavc.gov/internal_operating_procedures.php',
        'Rules of the U.S. Court of Appeals for Veterans Claims Rules Governing Judicial Misconduct': 'http://www.uscourts.cavc.gov/judicial_misconduct.php',
    }

    for rule_name, url in sheet_links_4.items():
        resource = requests.get(url)
        soup = BeautifulSoup(resource.text, "html.parser")

        content_a = soup.find('a', class_='link_subsection')
        h1_element = soup.find('h1')
        text = h1_element.get_text(strip=True)
        print(text)
        pdf_url = 'http://www.uscourts.cavc.gov/' + content_a.get("href")
        print(pdf_url)
        pdf_response = requests.get(pdf_url)
        output_file_name = common_module.ret_file_name_full(source_id_4, location_id_4, rule_name, '.pdf')
        with open(output_file_name, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {output_file_name}")


# Execute all sections
process_rules_of_admission_and_practice()
process_e_filing_rules()
process_local_rules()
process_veterans_claims_local_rules()