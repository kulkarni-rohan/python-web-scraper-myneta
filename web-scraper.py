import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin

"""
The following 2 dictionaries are used to match the appropriate rows from the UI ( example get all the column names under Description from link 
such as this https://myneta.info/delhi2013/candidate.php?candidate_id=50 )

In order to improve the code, you need to include the exact string from the UI for whichever new field you encounter
"""

columns_to_be_printed = {
    "Cash": 0,
    "Deposits in Banks, Financial Institutions and Non-Banking Financial Companies": 0,
    "Bonds, Debentures and Shares in companies": 0,
    "NSS, Postal Savings etc": 0,
    "LIC or other insurance Policies": 0,
    "Personal Loans": 0,
    "Motor Vehicles (details of make, etc.)": 0,
    "Jewellery (give details weight value)": 0,
    "Other assets, such as values of claims / interests": 0,
    "Agricultural Land": 0,
    "Non Agricultural Land": 0,
    "Buildings": 0,
    "Houses": 0,
    "Others": 0,
}

reset_columns_to_be_printed = {
    "Cash": 0,
    "Deposits in Banks, Financial Institutions and Non-Banking Financial Companies": 0,
    "Bonds, Debentures and Shares in companies": 0,
    "NSS, Postal Savings etc": 0,
    "LIC or other insurance Policies": 0,
    "Personal Loans": 0,
    "Motor Vehicles (details of make, etc.)": 0,
    "Jewellery (give details weight value)": 0,
    "Other assets, such as values of claims / interests": 0,
    "Agricultural Land": 0,
    "Non Agricultural Land": 0,
    "Buildings": 0,
    "Houses": 0,
    "Others": 0,
}


"""
This is used to check if a particular row being checked in the code has a field matching the existing dictionary.

This is used such that we can efficiently write the value of a field under the appropriate column.
"""

def is_substring_present(input, dictionary):
    substring = str(input)
    for _iterate_index, key in enumerate(dictionary.keys()):
        print(key, substring)
        if substring in str(key):
            return key
    return ""


# Currently gets the link to the candidate page and extracts all the information in the dict, need to return the dict and append it in the form of an array

"""
This function takes in a url (example: https://myneta.info/delhi2013/candidate.php?candidate_id=50) and gets all the row information present
in the 3 tables where 2 are for assets and one for liabilities

The one thing where this can fail is when there are extra tables before or in between the 3 tables. 

To tackle that, you need to find the exact index of the table and add / replace it in the line `for index in [1, 2, 3]`
"""

def get_candidate_page_information_to_csv(url):
    columns_to_be_printed = reset_columns_to_be_printed
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find_all("table", class_="table1")
    # The following 3 lines are the indices of the tables for any person 
    # in the https://myneta.info/karnatka2008/index.php?action=show_constituencies&state_id=2 table
    details_of_movable_assets_table_index = 1
    details_of_immovable_assets_table_index = 2
    details_of_liabilities_table_index = 3

    for index in [1, 2, 3]:
        rows = table[index].find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            row_data = []
            for cell in cells:
                cell_contents = cell.contents
                if len(cell_contents) == 2 and cell_contents[1].name == "span":
                    cell_text = cell_contents[0].text.strip()
                else:
                    cell_text = cell.text.strip()
                row_data.append(cell_text)

            key1 = is_substring_present(row_data[1], columns_to_be_printed)
            # print("ROHAN: ", key1)
            # print("TEMP: ",row_data)
            if key1 != "" and row_data[-1] != "Nil":
                columns_to_be_printed[key1] = row_data[-1]

            key2 = is_substring_present(row_data[0], columns_to_be_printed)
            if key2 != "" and row_data[-1] != "Nil":
                columns_to_be_printed[key2] = row_data[-1]
    return columns_to_be_printed


"""
This function takes in a link for a state with a specific year and then traverses to the list of cadidates for all the costituencies

@param url: string 
"""


def get_candidate_list_from_state_with_year(url):
    response = requests.get(url)
    # Get the html code for the link provided
    soup = BeautifulSoup(response.content, "html.parser")
    # This pattern is used to find all the constituencies ( example: Bagalkot)
    pattern = re.compile(r"index\.php\?action")
    # This contains all the elements which have the class `title` and enclosed within `h5`. This probably needs to be updated for the different states.
    constituencies_links = []
    for div in soup.find_all("h5", class_="title"):
        link = div.find_all("a", href=pattern)
        constituencies_links.append(link) if link is not None and len(
            link
        ) != 0 else None

	# `texts` contains the links for each of the constituencies found in the above code  
    texts = []
    for link in constituencies_links:
        texts.append(link[0].get("href"))  # Get the redirection based url
    
    # This needs to be updated and put the response in a `for` loop to go over all the constituencies. Currently it only writes for the second one
    # Second since the index starts from 0. So 0 stands for the first constituency. 
    response = requests.get(
        urljoin(url, texts[1])
    )  # urljoin since the `constituencies_links` are pointers on top of the original link.
    html_content = response.content
    
    # Get the html content for the page (example: https://myneta.info/karnatka2008/index.php?action=show_constituencies&state_id=2)
    new_soup = BeautifulSoup(html_content, "html.parser")

    tables = new_soup.find("table", id="table2")
    pattern2 = re.compile(r"candidate\.php\?candidate_id")
    
    # Get all the links for the candidate list table which is `table2``
    candidate_links = []
    for div in tables.find_all("td", recursive=True):
        link = div.find_all("a", href=pattern2)
        candidate_links.append(link) if link is not None and len(link) != 0 else None
    rows = tables.find_all("tr")

    index = 0

	# These are the headings of the table with the cadidate list. (Example: https://myneta.info/karnatka2008/index.php?action=show_constituencies&state_id=2)
	# It is the `List of Candidates (Constituency)` table from the above url.
    heading = [
        "Sno",
        "Candidate",
        "Party",
        "Criminal Cases",
        "Education",
        "Age",
        "Total Assets",
        "Liabilities",
    ]

	# Change the file name when changing the url
	# This logic below would match the row read from the url (example: https://myneta.info/karnatka2008/candidate.php?candidate_id=9)
	# and using the dictionary to get the exact column matching to update the csv file with the appropriate value.
    with open("result.csv", mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for row in rows:
            # Find all the table cells within the row
            cells = row.find_all("td")

            # Extract the text content from each cell and add it to a list
            # row_data = [cell.text.strip() for cell in cells]
            row_data = []

            for cell in cells:
                # Ignore the inner <span> tags while considering the outer <td> tags
                cell_contents = cell.contents
                if len(cell_contents) == 2 and cell_contents[1].name == "span":
                    cell_text = cell_contents[0].text.strip()
                else:
                    cell_text = cell.text.strip()
                row_data.append(cell_text)
            if index == 0:
                row_data.extend(heading)
                row_data.extend(columns_to_be_printed.keys())
            else:
                additional_column_data = get_candidate_page_information_to_csv(
                    urljoin(url, candidate_links[index - 1][0].get("href"))
                )
                row_data.extend(additional_column_data.values())
            index += 1
            writer.writerow(row_data)


"""
Change the `url` to the desired state with the year and you would get all the required information in a new file. 
"""
url = "https://myneta.info/karnatka2008/"


"""
Things needed to be done after changing the `url` and before running this code.
1. Change the file name which is hardcoded in the function `get_candidate_list_from_state_with_year`.
2. Ensure that all the description from all the candidates for that particular state and year are present in the dictionary present above. example: Cash
"""
get_candidate_list_from_state_with_year(url)
