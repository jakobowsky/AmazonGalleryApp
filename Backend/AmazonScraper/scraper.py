import time
import json
import os
import random
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from AmazonScraper.scraper_config import (
    get_web_driver_options,
    get_chrome_web_driver,
    set_browser_as_incognito,
    set_ignore_certificate_error,
    set_automation_as_head_less,
    CATEGORIES,
    DIRECTORY,
    CURRENCY,
    BASE_URL
)


class Reporter:
    def __init__(self, categories, base_url, currency, directory):
        self.categories = categories
        self.base_url = base_url
        self.currency = currency
        self.directory = f'{os.path.dirname(os.path.abspath(__file__))}/{directory}'

    def run(self):
        # self.generate_report('PS4')  # <---- single category
        self.run_bot_on_all_categories()

    def run_bot_on_all_categories(self):
        for category in self.categories:
            self.generate_report(category)
            pause = random.randint(5, 7)
            print(f"Sleeping for {pause}...")
            time.sleep(pause)

    def generate_report(self, category):
        data = self.get_data_from_category(category)
        full_directory = f'{self.directory}/{category}.json'
        report = {
            'date': self.get_now(),
            'category': category,
            'currency': self.currency,
            'base_link': self.base_url,
            'products': data
        }
        print(f"Creating report for {category}...")
        if not os.path.exists(full_directory):
            os.makedirs(os.path.dirname(full_directory), exist_ok=True)
        with open(full_directory, 'w') as f:
            json.dump(report, f)
        print(f"Done for {category}...")

    @staticmethod
    def get_now():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def get_data_from_category(self, category):
        scraper = AmazonScraper(category, self.base_url, self.currency)
        data = scraper.run()
        return data


class AmazonScraper:
    def __init__(self, search_term, base_url, currency):
        self.search_term = search_term
        self.base_url = base_url
        self.currency = currency
        options = get_web_driver_options()
        # set_automation_as_head_less(options)
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver = get_chrome_web_driver(options)
        self.currency = currency

    def run(self):
        print("Starting Script...")
        print(f"Looking for {self.search_term} products...")
        time.sleep(2)
        links = self.get_products_links()
        if not links:
            print(f"Stopped script for {self.search_term}.")
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products...")
        products = self.get_products_info(links)
        print(f"Got info about {len(products)} products...")
        self.driver.quit()
        return products

    def get_products_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_xpath('//*[@id="twotabsearchtextbox"]')
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(2)  # wait to load page
        pages_to_scrape = [f'{self.driver.current_url}&page={number}' for number in range(1, 4)]
        links = []
        for page in pages_to_scrape:
            links += self.get_products_links_from_page(page)
            time.sleep(random.randint(4, 8))
        return links

    def get_products_links_from_page(self, page):
        self.driver.get(page)
        print(f"Current url: {self.driver.current_url}")
        time.sleep(2)
        result_list = self.driver.find_elements_by_class_name('s-result-list')
        links = []
        try:
            results = result_list[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute('href') for link in results]
            return links
        except Exception as e:
            print("Didn't get any products...")
            print(e)
            return links

    def get_products_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins[:10]:
            product = self.get_single_product_info(asin)
            time.sleep(random.randint(1, 2))
            if product:
                products.append(product)
        return products

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_single_product_info(self, asin):
        print(f"Product ID: {asin} - getting data...")
        product_short_url = self.shorten_url(asin)
        self.driver.get(f'{product_short_url}?language=en_GB')
        time.sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        photo = self.get_photo_url()
        if title and seller and price:
            product_info = {
                'asin': asin,
                'url': product_short_url,
                'title': title,
                'seller': seller,
                'price': price,
                'photo': photo
            }
            return product_info
        return None

    def get_photo_url(self):
        try:
            return self.driver.find_element_by_id('landingImage').get_attribute('src')
        except Exception as e:
            print(e)
            print(f"Can't get photo of a product - {self.driver.current_url}")
            return None

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f"Can't get title of a product - {self.driver.current_url}")
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('bylineInfo').text
        except Exception as e:
            print(e)
            print(f"Can't get seller of a product - {self.driver.current_url}")
            return None

    def get_price(self):
        price = None
        try:
            price = self.driver.find_element_by_id('priceblock_ourprice').text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                availability = self.driver.find_element_by_id('availability').text
                if 'Available' in availability:
                    price = self.driver.find_element_by_class_name('olp-padding-right').text
                    price = price[price.find(self.currency):]
                    price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
        except Exception as e:
            print(e)
            print(f"Can't get price of a product - {self.driver.current_url}")
            return None
        return price

    @staticmethod
    def get_asin(product_link):
        return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]

    def shorten_url(self, asin):
        return self.base_url + 'dp/' + asin

    def convert_price(self, price):
        price = price.split(self.currency)[1]
        try:
            price = price.split("\n")[0] + "." + price.split("\n")[1]
        except:
            Exception()
        try:
            price = price.split(",")[0] + price.split(",")[1]
        except:
            Exception()
        return float(price)


def main():
    reporter = Reporter(CATEGORIES, BASE_URL, CURRENCY, DIRECTORY)
    reporter.run()


if __name__ == '__main__':
    main()
