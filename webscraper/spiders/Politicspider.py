#Import libraries
import scrapy
from selenium import webdriver
from scrapy.selector import Selector
import pandas as pd
import datetime

class PoliticItem(scrapy.Item):
    Time = scrapy.Field()
    Title = scrapy.Field()
    Description = scrapy.Field()
    Link = scrapy.Field()

class politicspider(scrapy.Spider):
    name = 'politicspider'

    custom_settings = {
        'FEED_URI': 'webscraper/output/geopolitics.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_TRUNCATE': True,
        'CONCURRENT_REQUESTS': 8,
    }
    #Set boundaries for the spider
    def __init__(self, current_date, days_year, *args, **kwargs):

        super(politicspider, self).__init__(*args, **kwargs)
        self.current_date = current_date
        self.days = days_year

        # Set up the Selenium driver
        self.driver = webdriver.Chrome()

        # Initialize the items list
        self.scraped_page = []
        self.scraped_data = []
        self.parsed_date = []
        self.scope = 1

    #set range for number of pages to scrape
    def start_requests(self):
        for i in range(1, self.scope+1): 
            self.scope = self.scope + 1
            yield scrapy.Request(url=f'https://www.reuters.com/news/archive/politicsNews?view=page&page={i}&pageSize=10', callback=self.parse)

        # Calculate the range for scraping (one year from the current date)
        start_date = self.current_date
        end_date = start_date - datetime.timedelta(days=self.days)
        self.end_date = end_date

    def parse(self, response):
        # Load the page using Selenium and Extract the page content using Scrapy selectors
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)

        # Extract all article elements
        articles = sel.css('article')
        for article in articles:
            item = PoliticItem()
            item['Link'] = 'https://www.reuters.com'+ article.css('a::attr(href)').get()
            item['Description'] = article.css('p::text').get()
            if item['Description'] is None:
                continue
            yield scrapy.Request(item['Link'] , callback=self.parse_article, meta={'item': item})

        self.scope += 1
        yield scrapy.Request(url=f'https://www.reuters.com/news/archive/politicsNews?view=page&page={self.scope}&pageSize=10', callback=self.parse)

    # Extract the title and time
    def parse_article(self, response):
        item = response.meta['item']
        sel = Selector(text=response.text)
        item['Title'] = sel.css('h1::text').get()
        time_elements = sel.css('span.date-line__date__23Ge-::text').getall()
        time_elements2 = sel.css('time::text').getall()
        time_elements3 = sel.css('div.published::text').getall()
        time_elements4 = sel.css('p.scrollytelling-time::text').getall()    
        if time_elements:
            item['Time'] = time_elements[0] + " " + time_elements[1]
        elif time_elements2:
            item['Time'] = time_elements2[0] + " " + time_elements2[1]
        elif time_elements3:
            item['Time'] = time_elements3
        elif time_elements4:
            for time_element in time_elements4:
                if 'Filed:' in time_element:
                    item['Time'] = time_element.replace('Filed: ', '')
            item['Title'] = sel.css('title::text').get()
        else:
            return
        # Convert the article date to a datetime.date object
        self.parsed_date = datetime.datetime.strptime(item['Time'], "%B %d, %Y %I:%M %p %Z").date()

        # Compare the parsed date with the max_date
        if self.parsed_date < self.end_date:
            self.scope = self.scope - 1
            # Reached the maximum date, stop scraping
            return
        else:
            # Add the item to the items list
            self.scraped_page.append(item)
            # Append the scraped data for the current page to the overall scraped data list
            self.scraped_data.extend(self.scraped_page)
            # Reset the scraped page list for the next page
            self.scraped_page = []
            self.parsed_date = []

    def close (self, reason):
        # Create a Pandas DataFrame
        df = pd.DataFrame(self.scraped_data, columns=['Time','Title', 'Description', 'Link'])
        df['Datetime'] = pd.to_datetime(df['Time'])
        # Sort the DataFrame by the Datetime column in descending order
        df_sorted = df.sort_values(by='Datetime', ascending=False)
        # Export the sorted DataFrame to a CSV file
        df_sorted.to_csv('webscraper/output/geopolitics.csv', index=False)
        # Close the Selenium driver when the spider finishes
        self.driver.quit()

    # scrapy crawl politicspider