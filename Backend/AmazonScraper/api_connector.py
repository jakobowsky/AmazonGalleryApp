from AmazonScraper.scraper_config import API_BASE_URL, DIRECTORY
import json
import os
import requests
from os import listdir
from os.path import isfile, join


class ApiConnector:
    """
    1. Iterate through reports
    2. Get data from every report
    3. Push Data to db
    """

    def __init__(self, api_base_url, directory):
        self.api_base_url = api_base_url
        self.headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        self.directory = f"{os.path.dirname(os.path.abspath(__file__))}/{directory}"
        self.file_extension = '.json'

    def run(self):
        files = self.report_files()
        self.send_data_to_api(files)

    def report_files(self):
        onlyfiles = [f for f in listdir(
            self.directory) if isfile(join(self.directory, f))]
        return [f for f in onlyfiles if f.endswith(self.file_extension)]

    def send_data_to_api(self, files):
        for file in files:
            data = self.get_data_from_file(file)
            if self.post_request_api(data):
                print("Data Updated")
            else:
                print("Error occurred")

    def post_request_api(self, data):
        link = f"{self.api_base_url}add-products/"
        body = {
            'category': data.get('category'),
            'products': data.get('products'),
            'date': data.get('date')
        }
        r = requests.post(link, json=body, headers=self.headers)
        if r.status_code == 200:
            print(r.text)
            return True
        return False

    def get_data_from_file(self, file):
        with open(f'{self.directory}/{file}') as f:
            data = json.loads(f.read())
        return data


def main():
    api = ApiConnector(API_BASE_URL, DIRECTORY)
    api.run()


if __name__ == '__main__':
    main()
