from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
import random
import csv

def random_delay(min_seconds, max_seconds):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)



class Amazon_Scrape:
    def __init__(self, head):
        # Set up Firefox options
        firefox_options = Options()
        if not head:
            firefox_options.add_argument("--headless")

        # Path to your GeckoDriver and Firefox binary
        gecko_path = r"C:\Users\ezrag\Desktop\Data Stuff\.data\geckodriver.exe"
        firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        # Initialize the Service and Options
        service = Service(executable_path=gecko_path)
        firefox_options.binary_location = firefox_binary_path
        # Initialize the WebDriver with the correct options
        self.driver = webdriver.Firefox(service=service, options=firefox_options)
        self.product_data = {}
        self.url = ""
        self.read_more_urls = []


    def load_site(self, link):
        # Open Amazon search results page
        self.url = link
        self.driver.get(self.url)
        # Allow time for the page to load
        time.sleep(2)


    def extract_info(self):
        self.product_data.clear()
        self.driver.maximize_window()
        #Extract product information
        ##TITLE
        try:
            # Example of extracting the product title
            self.product_data["title"] = self.driver.find_element(By.ID, 'productTitle').text


        except Exception as TitleError:
            self.product_data["title"] = ""
            print("Title Error:", TitleError)

        ##PRICE (Actual)
        try:
        # Extract the whole and decimal parts of the price
            whole_part = self.driver.find_element(By.CLASS_NAME, 'a-price-whole').text
            decimal_part = self.driver.find_element(By.CLASS_NAME, 'a-price-fraction').text
            
            # Remove any commas from the whole part and convert to float
            whole_part = whole_part.replace(',', '')
            price = float(whole_part + '.' + decimal_part)

            self.product_data["price_actual"] = price
        except Exception as e1:
            self.product_data["price_actual"] = ""
            print("Actual Price Error:", e1)

        ##PRICE (Listing)
        try:
            # Locate the element containing the operating system information
            # Adjust the CSS selector based on the actual page structure
            price_info = self.driver.find_element(By.CLASS_NAME, 'a-price.a-text-price')
        #This isn't working as needed
            # Extract and print the text of the operating system element
            price_list = price_info.text.splitlines()
            price_list = float(price_list[-1][1:])
            self.product_data["price_list"] = price_list

        except Exception as e:
            self.product_data["price_list"] = "Check Page"
            print("Listing Price not found. POssible not exist on page", e)

        ##PRODUCT DATA
        
        key_element = ""
        try: 
            element = self.driver.find_element(By.ID, 'poToggleButton')
            element = element.find_element(By.CLASS_NAME, "a-expander-prompt")
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()

            see_more = self.driver.find_element(By.CLASS_NAME, "a-normal.a-spacing-micro")
            rows = see_more.find_elements(By.CSS_SELECTOR, 'tr.a-spacing-small')
            for row in rows:
                try:
                    key_element = row.find_element(By.CLASS_NAME, 'a-span3')
                    value_element = row.find_element(By.CLASS_NAME, 'a-span9')
                # Extract the labels and values
                    key_text = key_element.text
                    value_text = value_element.text
                    if value_text.__contains__("See more"):
                        self.read_more_urls.append(self.driver.current_url)
                        see_more_detailed = row.find_element(By.CLASS_NAME, "a-popover-trigger.a-declarative")
                        see_more_detailed.click()
                        time.sleep(3)
                        popover_element = self.driver.find_elements(By.CLASS_NAME, "a-popover-inner")
                        window_size = self.driver.get_window_size()
                        # Calculate the coordinates for the left-middle side of the screen
                        x = window_size['width'] * 0.1  # 10% from the left side
                        y = window_size['height'] * 0.5  # 50% from the top, so middle

                        # Create ActionChains object to perform the click
                        actions = ActionChains(self.driver)
                        actions.move_by_offset(x, y).click().perform()
                    self.product_data[key_text] = value_text

                    
                except:
                    pass

            # Print the values
        except:
            if key_element != "":
                self.product_data[key_text] = value_text


        key_element = ""
        try: 
            self.driver.execute_script("window.scrollBy(0, 100);")
            table = self.driver.find_element(By.ID, 'productDetails_detailBullets_sections1')
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                key = row.find_element(By.TAG_NAME, "th").text
                val = row.find_element(By.TAG_NAME, "td").text
                print(key + " - " + val)  
                self.product_data[key] = val

            # Print the values
        except:
            if key_element != "":
                self.product_data[key_text] = value_text
        ##AVG Rvw Score (Listing)
        #Must make sure reaching correct area and stripping correct info
        try:
            # Locate the element containing the average review score
            # Adjust the CSS selector based on the actual page structure
            test = self.driver.find_element(By.ID, 'acrPopover').find_element(By.CLASS_NAME, "a-size-base.a-color-base")
            rvw_avg = float(test.text)
            # Extract and print the text of the operating system element
            self.product_data["rvw_avg"] = rvw_avg
            print("Average Review Score:", self.product_data["rvw_avg"])

        except Exception as e:
            self.product_data["rvw_avg"] = "Unknown"
            print("Element not found:", e)
        
                
    def get_lib(self):
        return self.product_data
    
    def clear_lib(self):
        self.product_data.clear()
        self.product_data.clear

    def quit_web(self):
        # Close the WebDriver
        self.driver.quit()
        with open("read_more_urls.txt", 'w') as file:
            file.write('\n \n'.join(self.read_more_urls))





class Amazon_100_Scrape:
    def __init__(self, link, output_name):
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        # firefox_options.add_argument("--headless")
        # Path to your GeckoDriver and Firefox binary
        gecko_path = r"C:\Users\ezrag\Desktop\Data Stuff\.data\geckodriver.exe"
        firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        # Initialize the Service and Options
        service = Service(executable_path=gecko_path)
        firefox_options.binary_location = firefox_binary_path

        # Initialize the WebDriver with the correct options
        driver = webdriver.Firefox(service=service, options=firefox_options)
        self.scraper = Amazon_Scrape(True)
        self.scraper = driver
        self.scraper.get(link)
        self.output_links = []
        self.output_name = output_name
        self.scrape_runner = Amazon_Scrape(False)

    def quit_web(self):
        # Close the WebDriver
        self.scraper.quit()
    
    def scrape(self):
        print("loading")
        for i in range(2):  # Run this loop to attempt to retrieve all the links.          
            while True:
                last_height = self.scraper.execute_script("return document.body.scrollHeight")                
                scroll_pause_time = 3  # Adjust this as needed for your connection speed
                 # Scroll up a bit (by 1000 pixels, adjust as needed)
                self.scraper.execute_script("window.scrollBy(0, -1000);")
                time.sleep(scroll_pause_time)
                # Scroll back down to the bottom
                self.scraper.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

                
                # Extract the items after each scroll
                item_table = self.scraper.find_elements(By.CLASS_NAME, "a-link-normal.aok-block")
                new_links = [item.get_attribute('href') for item in item_table if item.get_attribute('href') not in self.output_links]
        

                # If new links are found, add them to the list
                if new_links:
                    self.output_links.extend(new_links)
                    print(f"Found {len(new_links)} new links.")
                else:
                    # If no new links are found after a scroll, break the loop
                    break
                
                # Calculate new scroll height and compare with the last scroll height
                new_height = self.scraper.execute_script("return document.body.scrollHeight")
                time.sleep(scroll_pause_time)
                if new_height == last_height:
                    break
                last_height = new_height
                # Click 'Next' button to load more items

                
            print(f"Total links found: {len(self.output_links)}")
            for count, link_url in enumerate(self.output_links):
                print(f"{count}: {link_url}")
            
            self.scraper.find_element(By.CLASS_NAME, "a-last").click()

        file_path = os.path.join(r'C:\Users\ezrag\Desktop\Data Stuff', self.output_name)+".txt"
        self.save_links_to_file(self.output_links, file_path)

    def save_links_to_file(self, links, file_path):
        """Save a list of links to a text file, separated by commas."""
        with open(file_path, 'w') as file:
            file.write(','.join(links))
        print(f"Links saved to {file_path}")

    def load_links_from_file(self, file_path):
        """Load a list of links from a text file where they are separated by commas."""
        with open(file_path, 'r') as file:
            content = file.read()
            links = content.split(',')
        return links
    


def lib_to_csv(library, output_name):
    # Check if file exists
    if os.path.exists(output_name):
        # If it exists, load existing data
        existing_df = pd.read_csv(output_name)
    else:
        existing_df = pd.DataFrame()
    # Convert the list of dictionaries to a DataFrame
    new_df = pd.DataFrame(library)
    
    # Combine with existing data, aligning columns
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    # Save to CSV
    combined_df.to_csv(output_name, index=False)
    print(f"Data exported to {output_name}")

def create_spreadsheet(data_dict, output_dict, output_filename):
    # Convert the dictionary of dictionaries to a DataFrame
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'URL'}, inplace=True)
    # Load existing CSV data if it exists, or start fresh if it doesn't
    try:
        existing_df = pd.read_csv('output_file.csv')
        # Combine existing data with the new data
        combined_df = pd.concat([existing_df, df], ignore_index=True, sort=False)
    except FileNotFoundError:
        combined_df = df

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(output_filename, index=False)
    return output_dict
   

def scrape_links():
    #must use best selling top 100 links:
    links_to_scrape = []
    print("loading")
    links_to_scrape.append(Amazon_100_Scrape("https://www.amazon.com/gp/bestsellers/electronics/7939901011?ref_=Oct_d_obs_S&pd_rd_w=QWPtd&content-id=amzn1.sym.3077d44e-b53e-482e-b605-9df89d795020&pf_rd_p=3077d44e-b53e-482e-b605-9df89d795020&pf_rd_r=X1JJFG18PFZX54YFXF3F&pd_rd_wg=0xOHJ&pd_rd_r=ee42105d-1fdc-484c-aefe-0cb4ff7be449",
                                           "output_best_watch"))
    #links_to_scrape.append(Amazon_100_Scrape("https://www.amazon.com/Best-Sellers-Electronics-Smart-Rings/zgbs/electronics/10048711011/ref=zg_bs_nav_electronics_2_7939901011",
    #                                       "output_best_ring"))
   # links_to_scrape.append(Amazon_100_Scrape("https://www.amazon.com/Best-Sellers-Electronics-Smart-Glasses/zgbs/electronics/10048708011/ref=zg_bs_nav_electronics_2_7939901011",
    #                                       "output_best_glasses"))
    #links_to_scrape.append(Amazon_100_Scrape("https://www.amazon.com/Best-Sellers-Electronics-Activity-Fitness-Trackers/zgbs/electronics/5393958011/ref=zg_bs_nav_electronics_2_10048706011",
   #                                        "output_best_fittrack"))
    
    for link in links_to_scrape:
        print("loading")
        link.scrape()
        link.quit_web()
    
    
def main():
    direct = r'C:\Users\ezrag\Desktop\Data Stuff'
    output_links = []
    links_to_scrape_txt = ["output_best_fittrack.txt"]#,"output_best_ring.txt", "output_best_glasses.txt", "output_best_fittrack.txt"]
    for item in links_to_scrape_txt:
        output_links.append(direct+"\\"+item)
        print(output_links)
    output_lib = {}
        
    scraper = Amazon_100_Scrape("https://www.google.com", "gog")
    links_to_scrape = []
    for item in links_to_scrape_txt:
        links_to_scrape.extend(scraper.load_links_from_file(item))
    scraper.quit_web()

    #pull data from each link
    listing_scraper = Amazon_Scrape(False)
    #listing_scraper = Amazon_Scrape(True)

    output_dict = pd.DataFrame()
    cnt = 0
    for link in links_to_scrape:
        listing_scraper.clear_lib()
        listing_scraper.load_site(link)
        listing_scraper.extract_info()
        output_lib[link] = listing_scraper.get_lib().copy() 
        output_dict = create_spreadsheet(output_lib, output_dict,"output-fittrack.csv")
        print(cnt)
        cnt+=1
    listing_scraper.quit_web()
    


    



main()