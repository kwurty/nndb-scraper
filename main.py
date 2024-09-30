import requests
import csv
import json

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

def parse_table(table):
    persons = []
    rows = table.find_all('tr')
    for row in rows:
        name = row.find_all('td')[0].text
        occupation = row.find_all('td')[1].text
        description = row.find_all('td')[2].text
        birth = row.find_all('td')[3].text
        death = row.find_all('td')[4].text
        persons.append({
            'Name': name,
            'Occupation': occupation,
            'Description': description,
            'Birth': birth,
            'Death': death
        })
    return persons

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
