import requests
import csv
import json
import mysql.connector

from bs4 import BeautifulSoup

def get_urls_from_csv(path):
    """Read URLs from a CSV file and return them as a list."""
    urls = []
    with open(path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the URL is in the first column
            if row:
                urls.append(row[0])
    return urls

def fetch_html(url):
    """Fetch a URL and return the response status."""
    try:
        response = requests.get(url)
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
def parse_html(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) > 5:
        table = tables[5]
        return table

def format_name(name):
    # Define suffixes to check for
    suffixes = {'Jr.', 'Sr.', 'II', 'III', 'IV', 'V'}
    
    # Remove any leading or trailing whitespace
    name = name.strip()
    
    # Split the full name into parts
    name_parts = name.split(',')
    
    # Handle the case where there's a suffix
    if len(name_parts) > 1:
        # Extract the name before the comma
        name_part = name_parts[0].strip()
        suffix_part = name_parts[1].strip()
        # Check if the suffix is valid
        if any(suffix in suffix_part for suffix in suffixes):
            # Handle the last name extraction
            suffixes_found = [suffix for suffix in suffixes if suffix in suffix_part]
            last_name = name_part.split()[-1]  # Take the last part before the comma
        else:
            last_name = name_part.split()[-1]
    else:
        name_part = name_parts[0].strip()
        last_name = name_part.split()[-1]

    # Split the name part into individual components
    name_parts = name_part.split()
    
    # Handle the case where there are no names
    if not name_parts:
        return None, None

    # The first part is considered the first name
    first_name = name_parts[0]

    # If the first name is an initial, return only the initial
    if len(first_name) == 2 and first_name[1] == '.':
        first_name = first_name[0]  # Keep only the initial
    
    return first_name, last_name

def parse_table(table):
    persons = []
    rows = table.find_all('tr')
    for row in rows:
        name = row.find_all('td')[0].text
        occupation = row.find_all('td')[1].text
        description = row.find_all('td')[2].text
        birth = row.find_all('td')[3].text
        death = row.find_all('td')[4].text
        firstname, lastname = format_name(name)
        persons.append({
            'Name': name,
            'First_Name': firstname,
            'Last_Name': lastname,
            'Occupation': occupation,
            'Description': description,
            'Birth': birth,
            'Death': death
        })
    return persons

def insert_data(data):
    # MySQL database connection configuration
    db_config = {
        'user': 
        'password': ,
        'host': 
        'database': 
    }
    connection = None
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # SQL insert statement
        insert_query = """
        INSERT INTO People (Name, First_Name, Last_Name, Occupation, Description, Birth, Death)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Loop through each item in the data
        for item in data:
            # Prepare data for insertion
            values = (
                item['Name'],
                item['First_Name'],
                item['Last_Name'],
                item['Occupation'],
                item['Description'],
                item['Birth'],
                item['Death']
            )

            # Execute the insert statement
            cursor.execute(insert_query, values)

        # Commit the transaction
        connection.commit()
        print("Data inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
def main():
    filename = 'urls.csv'
    urls = get_urls_from_csv(filename)
    persons = []
    
    for url in urls:
        response = fetch_html(url)
        if response and response.status_code is not None:
            print(f"URL: {url} - Status Code: {response.status_code}")
        if response and response.status_code == 200:
            table = parse_html(response)
            people = parse_table(table)
            persons.extend(people)
    
    with open('json_data', 'w') as json_file:
        json.dump(persons, json_file, indent=2)

if __name__ == '__main__':
    main()
