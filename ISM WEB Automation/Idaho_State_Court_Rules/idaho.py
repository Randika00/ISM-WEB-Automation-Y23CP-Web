import requests
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import aspose.pdf


url ="https://isb.idaho.gov/bar-counsel/irpc/"

sheet_links = {'Idaho Rules of Professional Conduct': 'https://isb.idaho.gov/bar-counsel/irpc/'}
                # 'Idaho Rules of Civil Procedure': 'https://judicial.alabama.gov/library/CivilProcedure',
                # 'Idaho Rules of Evidence':'https://judicial.alabama.gov/library/CriminalProcedure',
                # 'Idaho Criminal Rules':'https://judicial.alabama.gov/library/RulesEV'}

# resource = requests.get(url)
# soup = BeautifulSoup(resource.text, "html.parser")
# # print(resource.status_code)
#
# # print(soup)
#
# link = soup.find('a',class_ = 'wp-block-button__link')
# print(link)

pdf_folder = 'pdf'
os.makedirs(pdf_folder, exist_ok=True)
error_dict={}
error_list=[]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def get_pdf(pdf_url):
    filename = re.search(r'/([^/]+)\.pdf$', pdf_url)
    if filename:
        filename = filename.group(1) + '.pdf'
        # Combine with the pdf_folder path
        pdf_path = os.path.join(pdf_folder, filename)
        # Download the PDF into the pdf_folder
        pdf_response = requests.get(pdf_url, headers=headers)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {pdf_path}")
    else:
        print("Could not determine filename from URL:", pdf_url)

def getting_rules(tr_element):
    for td_data in tr_element:
        try:
            td_elements = td_data.find_all('td')
            left_evidence = td_elements[0].text.strip()
            right_evidence = td_elements[1].text.strip()
            first_rule_name=left_evidence+right_evidence

            rule_name = first_rule_name.upper()
            rule_name = re.sub(r'\s+', ' ', rule_name)
            rule_name = re.sub(r'[^a-zA-Z0-9]+', '', rule_name)
            with open('Idaho.txt', 'r', encoding='utf-8') as read_file:
                read_content = read_file.read().strip().upper()
                read_content = re.sub(r'[^a-zA-Z0-9]+', '', read_content)

                if rule_name in read_content:
                   pdf_url = "https://isc.idaho.gov" + str(td_elements[0].find('a')['href'])
                   get_pdf(pdf_url)
                else:
                   right_evidence_evidence = td_elements[1].text.strip()
                   rule_name = right_evidence_evidence.upper()
                   rule_name = re.sub(r'\s+', ' ', rule_name)
                   rule_name = re.sub(r'[^a-zA-Z0-9]+', '', rule_name)
                   if rule_name in read_content:
                      pdf_url = "https://isc.idaho.gov" + str(td_elements[0].find('a')['href'])
                      get_pdf(pdf_url)
                   else:
                        pass
                        print("==========================================", first_rule_name)

        except Exception as e:
            error_list.append(e)

    input_folder = 'pdf'

    # Output folder for HTML files
    output_folder = 'out_html'

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through PDF files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(input_folder, filename)
            pdf_document = aspose.pdf.Document(pdf_file)

            # Generate an HTML filename by replacing the '.pdf' extension with '.html'
            html_filename = os.path.splitext(filename)[0] + '.html'
            html_file = os.path.join(output_folder, html_filename)

            # Save the PDF as HTML in the output folder
            pdf_document.save(html_file, aspose.pdf.SaveFormat.HTML)

    print("Conversion completed.")

def get_link(url):
    response=requests.get(url)
    soup=BeautifulSoup(response.text,'html.parser')
    table_datas = soup.find('div', class_='rules-list-background')
    table_datas_evidence = soup.find('div', class_='lib_rules')
    if table_datas:
        return table_datas
    if table_datas_evidence:
        return table_datas_evidence


if os.path.exists('Idaho.txt'):
    for name, url in sheet_links.items():
        try:
            if name=='Idaho Rules of Professional Conduct':
                table_rows = get_link(url)
                table_rows=table_rows.find_all('tr')
                getting_rules(table_rows)
            else:
                table_rows = get_link(url)
                if name == 'Idaho Criminal Rules':
                    h4_element = table_rows('h4')
                    for h4_name in h4_element:
                        check_h4_element = ['Rule 8.4. Misconduct',
                               'Rule 8.5: Disciplinary Authority; Choice of Law']
                        if h4_name.text.strip() in check_h4_element:
                            if h4_name.text.strip() == 'APPENDIX OF FORMS':
                                a_element = h4_name.find('a')
                                new_link = 'https://isc.idaho.gov' + a_element['href']
                                new_table_rows = get_link(new_link)
                                new_table_rows = new_table_rows.find_all('tr')
                                getting_rules(new_table_rows)


        except Exception as e:
            error_list.append(e)
else:
     print("'alabama.txt' does not exist in the current directory.")



