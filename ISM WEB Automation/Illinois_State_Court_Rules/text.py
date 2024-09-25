import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

source_id = 'Illinois State Court Rules'



sheet_links = {
    'Rules of Evidence': 'https://www.illinoiscourts.gov/courts/supreme-court/courts-supreme-court-illinois-rules-of-evidence/',
    'Judicial Circuit Rules - 3rd Judicial Circuit Rules': 'https://www.madisoncountyil.gov/departments/circuit_court/about/local_rules_and_pro_hac_vice_information.php',

}

# for rule_name, url in sheet_links.items():
#     resource = requests.get(url)
#     soup = BeautifulSoup(resource.text, "html.parser")
#     print(resource.status_code)
#
#     # Attempt to find the table, handle the case where it's not found
#     try:
#         table = soup.find("table", {"id": "ctl04_gvRules"})
#         if table:
#             links = table.findAll('tr')
    #         for i in links:
    #      else:
    #           print(f"Table with ID 'ctl04_gvRules' not found on the page: {url}")
    #     except AttributeError as e:\
    #         print(f"An error occurred while scraping the page: {e}")
    #
    # links = soup.find_all("a")
    # for link in links:
    #     pdf_url = link.get("href", "")
    #     if pdf_url.endswith('.pdf'):
    #         pdf_response = requests.get(pdf_url, stream=True)
    #         if pdf_response.status_code == 200:
    #             # Create a filename based on the link's text or other information
    #             filename = ret_file_name_full(source_id, rule_name, link.text, '.pdf')
    #             with open(filename, 'wb') as pdf_file:
    #                 for chunk in pdf_response.iter_content(chunk_size=1024):
    #                     if chunk:
    #                         pdf_file.write(chunk)
    #             print(f"Downloaded: {filename}")
    #         else:
    #             print(f"Failed to download PDF from {pdf_url}")
#
