#Import libraries

import scrapy
from selenium import webdriver
from scrapy.selector import Selector
import pandas as pd
import datetime

class PortItem(scrapy.Item):
    Time = scrapy.Field()
    Area = scrapy.Field()
    Title = scrapy.Field()
    Description = scrapy.Field()
    Link = scrapy.Field()

class portspider(scrapy.Spider):
    name = 'portspider'

    custom_settings = {
        'FEED_URI': 'webscraper/output/portnews.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_TRUNCATE': True,
    }
    #Set boundaries for the spider
    def __init__(self, current_date, days_year, *args, **kwargs):

        super(portspider, self).__init__(*args, **kwargs)
        self.current_date = current_date
        self.days = days_year
    
        # Set up the Selenium driver
        self.driver = webdriver.Chrome()

        # Initialize the csv items list
        self.scraped_data = []
        self.scraped_links = set()
        # Initialize the temporary items list
        self.scraped_page = []
        self.parsed_date = []
        self.scope = 1

    #set range for number of pages to scrape
    def start_requests(self):

        for i in range(1, self.scope+1): 
            yield scrapy.Request(url=f'https://container-news.com/port-news/page/{i}', callback=self.parse)

        # Calculate the range for scraping (one year from the current date)
        start_date = self.current_date
        end_date = start_date - datetime.timedelta(days=self.days)
        self.end_date = end_date

    def parse(self, response):
        # Load the page using Selenium and Extract the page content using Scrapy selectors
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)

        # Loop through each article and extract link and title
        for article in sel.xpath('//div[@class="td-module-meta-info"]/h3/a'):
            item = PortItem()
            item['Link'] = article.xpath('./@href').get()
            # Check if the article link has already been scraped
            if item['Link'] not in self.scraped_links:
                item['Title'] = article.xpath('./@title').get()

                # Add the article link to the set of scraped links
                self.scraped_links.add(item['Link'])
                yield scrapy.Request(item['Link'], callback=self.parse_article, meta={'item': item})
            else:
                continue
        self.scope += 1
        yield scrapy.Request(url=f'https://container-news.com/port-news/page/{self.scope}', callback=self.parse)

    # Extract the time and description in the article
    def parse_article(self, response):
        item = response.meta['item']
        sel = Selector(text=response.text)
        item['Time'] = sel.xpath('//time/text()').get()
        item['Description'] = ' '.join(sel.xpath('//div[@class="tdb-block-inner td-fix-index"]/p/text()').getall()).strip()

        # Convert the article date to a datetime.date object
        self.parsed_date = datetime.datetime.strptime(item['Time'], "%B %d, %Y").date()

        # Compare the parsed date with the max_date
        if self.parsed_date < self.end_date:
            self.scope = self.scope - 1
            # Reached the maximum date, stop scraping
            return

        # Add the item to the items list
        self.scraped_page.append(item)
        # Append the scraped data for the current page to the overall scraped data list
        self.scraped_data.extend(self.scraped_page)
        # Reset the scraped page list for the next page
        self.scraped_page = []

    def close (self, reason):
        # Create a Pandas DataFrame
        df = pd.DataFrame(self.scraped_data, columns=['Time', 'Title', 'Description', 'Link'])
        df['Datetime'] = pd.to_datetime(df['Time'])
        # Sort the DataFrame by the Datetime column in descending order
        df_sorted = df.sort_values(by='Datetime', ascending=False)
        # Export the sorted DataFrame to a CSV file
        df_sorted.to_csv('webscraper/output/portnews.csv', index=False)
        # Close the Selenium driver when the spider finishes
        self.driver.quit()

    # scrapy crawl portspider