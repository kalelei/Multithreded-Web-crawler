# Yiğit Kaleli

import json
from audioop import mul
import time
import multiprocessing
from queue import Empty, Queue
from urllib.parse import urlparse,urljoin
import urllib.request
import requests
from bs4 import BeautifulSoup
import concurrent.futures




Amazon_list=[]
Trendyol_list=[]






class MultiThreadedCrawler: #Crawler object
    def __init__(self, seed_url):
        self.seed_url = seed_url
        self.root_url = '{}://{}'.format(urlparse(self.seed_url).scheme,
                                         urlparse(self.seed_url).netloc)

        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=10) #To able to read all roots concurently
        self.scraped_pages = set([])   #To check if the url visited before
        self.crawl_queue = Queue()
        self.crawl_queue.put(self.seed_url)  #At first adding the main URL to queue



    def scrape_info(self, html): #Scrape the page and getting information about items
        if(self.seed_url == "https://www.amazon.com.tr/s?k=basketbol+topu&sprefix=baske%2Caps%2C126&ref=nb_sb_ss_ts-doa-p_1_5"):
            soup = BeautifulSoup(html, "html.parser")
            print("---------AMAZON BASKETBALL PRICES SAVED---------")
            try:
                balls = soup.find_all("div", attrs={'class': 'sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20'})
                for ball in balls:
                    try:
                        price = ball.find("span", attrs={'class': 'a-price-whole'}).getText().strip().replace(',', '')
                    except:
                        price = "NA"

                    try:
                        ball_name = ball.find("a", attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).getText()
                    except:
                        ball_name = "NA"

                    json_data = {
                        "Name": ball_name,
                        "Price": price
                        }
                    
                    Amazon_list.append(json_data)
           
            except AttributeError:
                balls = "NA"

            with open('amazon.json', 'w', encoding='utf-8') as f:
                json.dump(Amazon_list, f, indent=8, ensure_ascii=False)
        

        else: #When url becomes trendyol
        
            soup = BeautifulSoup(html, "html.parser")
            print("---------TRENDYOL BASKETBALL PRICES SAVED---------")
            try:
                balls = soup.find_all("div", attrs={'class': 'p-card-wrppr'})
                for ball in balls:
                    try:
                        price = ball.find("div", attrs={'class': 'prc-box-dscntd'}).getText().strip().replace(',', '')
                    except:
                        price = "NA"

                    try:
                        ball_name = ball.find('span', attrs={'class': 'prdct-desc-cntnr-name hasRatings'})['title']
                    except:
                        ball_name = "NA"

                    json_data = {
                        "Name": ball_name,
                        "Price": price
                        }
                    
                    Trendyol_list.append(json_data)
           
            except AttributeError:
                balls = "NA"

            with open('trendyol.json', 'w', encoding='utf-8') as f:
                json.dump(Trendyol_list, f, indent=8, ensure_ascii=False)


    # def parse_links(self, html):                        #To able to check inner HTMLs of root HTML 
    #     soup = BeautifulSoup(html, 'html.parser')
    #     Anchor_Tags = soup.find_all('link', href=True)
        
    #     for link in Anchor_Tags:
    #         url = link['href']
            
    #         if url.startswith('/') or url.startswith(self.root_url):
    #             url = urljoin(self.root_url, url)
                
    #             if url not in self.scraped_pages:
    #                 self.crawl_queue.put(url)



    def scrape_page(self,url): #Getting request from page
        HEADERS={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.55"
        }
        try:
            res = requests.get(url, headers=HEADERS ,timeout=(3, 30))
            time.sleep(0.25)  #To get not banned or exceed request limit
            return res
        except requests.RequestException:
            return




    def scrapeCalls(self, res):
        result = res.result()
        
        if result and result.status_code == 200:
            #self.parse_links(result.content)
            self.scrape_info(result.content)


    def start_crawling(self):
        while True:
            try:
                print("\n Name of the current executing process :", multiprocessing.current_process().name, '\n')
                
                target_url = self.crawl_queue.get(60)
                if target_url not in self.scraped_pages: #Checking if the pages already crawled or not
                    print("Scraping URL: {}".format(target_url))
                    self.scraped_pages.add(target_url)   #Adding targerURL to scraped_pages list to not scrape it again 
                    
                    scrape = self.pool.submit(self.scrape_page, target_url)

                    scrape.add_done_callback(self.scrapeCalls)
                    return True
            
            except Empty:
                return 
            except Exception as e:
                print(e)
                continue
                    

def run(web_page):
        Web_crawl_obj = MultiThreadedCrawler(web_page)   #Creating crawling obj for each web-page
        Web_crawl_obj.start_crawling() 



#Trendyol & Amazon Basketball prices
if __name__ == '__main__':

    web_pages = ["https://www.amazon.com.tr/s?k=basketbol+topu&sprefix=baske%2Caps%2C126&ref=nb_sb_ss_ts-doa-p_1_5","https://www.trendyol.com/nike-x-b44"]  #later read it from file
    scraped_pages = []  #Check if page is already scraped
    
    no_of_threads = 2 #defining number of threads it is important to limit the number of worker threads in the thread pools to the number of asynchronous tasks you wish to complete

    with concurrent.futures.ThreadPoolExecutor(max_workers=no_of_threads) as executor:
        for web_page in web_pages:
            if web_page not in scraped_pages:
                print(f"\nThread starting for webpage: {web_page}")
                executor.submit(run,web_page)
                scraped_pages.append(web_page)
            else:
                continue
            
    




