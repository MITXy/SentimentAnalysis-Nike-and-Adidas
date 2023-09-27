import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import os
from selenium import webdriver
from  selenium.webdriver.common.by import By
from  selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

os.environ["PATH"] += r"C:/SeleniumDrivers"
url = "https://www.adidas.com/api/search/tf/taxonomy?sitePath=us&query=shoes"
html = requests.get(url=url)
print(html.text)
soup = BeautifulSoup()
output = json.load(html.text)


def find_shoe_review(shoe_number):
    
    url = "https://www.adidas.com/us"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(15)

    try:
        accept_button = driver.find_element(By.ID, "glass-gdpr-default-consent-accept-button")
        accept_button.click()
    except:
        print("Accept button not found!")

    search = driver.find_element(By.CSS_SELECTOR, '[data-auto-id="searchinput-desktop"]')
    search.click()
    search.send_keys("shoe")
    search.send_keys(Keys.ENTER)

    main_content = driver.find_element(By.ID, "main-content")
    products = main_content.find_elements(By.CSS_SELECTOR, '[class="grid-item"]')
    products[shoe_number].click()

    try:
        pop_up_button = driver.find_element(By.CSS_SELECTOR, 'button[name="account-portal-close"]')
        pop_up_button.click()
    except NoSuchElementException:
        ("print no pop up")

    try:
        driver.find_element(By.CSS_SELECTOR, '[style="position: absolute; top: 0px; left: 0px; width: 30px;\
        height: 30px; overflow: hidden; display: block;"]')
    
    except:
        print("Not Found")

    try:
        product_name = driver.find_element(By.CSS_SELECTOR, '[data-auto-id="product-title"]').get_attribute("innerHTML")
    except NoSuchElementException:
        product_name = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-title"]').get_attribute("innerHTML")

    try:
        product_price = driver.find_element(By.CSS_SELECTOR, '[id="gl-price-item"]').get_attribute("innerHTML")
    except NoSuchElementException:
        product_price = driver.find_element(By.CSS_SELECTOR, '[class="gl-price-item notranslate"]').get_attribute("innerHTML")
    
    try:
        product_colour = driver.find_element(By.CSS_SELECTOR, "[id=available-colors-label]").get_attribute("innerHTML")
    except NoSuchElementException:
        product_colour = driver.find_element(By.CSS_SELECTOR, '[class="skip-link___3E77n"]').get_attribute("innerHTML")
    
    try:
        review_drop_down = driver.find_element(By.CSS_SELECTOR, '[data-testid="dropdown"]')
        review_drop_down.click()
    except NoSuchElementException:
        review_drop_down = driver.find_element(By.CSS_SELECTOR, '[role="img"]')
        review_drop_down.click()
    except NoSuchElementException:
        review_drop_down = driver.find_element(By.ID, 'navigation-target-reviews')
        review_drop_down.click()
    for i in range (100):
        load_more_reviews = driver.find_element(By.CSS_SELECTOR, '[data-auto-id="ratings-load-more"]')
        load_more_reviews.click()


    try:
        read_mores = driver.find_elements(By.CSS_SELECTOR, '[data-auto-id="review-read-more-button"]')
    except:
         read_mores = driver.find_elements(By.CSS_SELECTOR, '[class="read-more___2dacS gl-link gl-label--m"]')


    for reading in read_mores[:400]:
        reading.click()

    heading = []
    messaging = []
    info = []

    #actual reviews
    reviews = driver.find_elements(By.CSS_SELECTOR, '[class="review___2sQiC gl-vspace-bpall-medium"]')
   
    for review in reviews:
        header = review.find_element(By.CSS_SELECTOR, '[class="gl-body gl-no-margin-bottom"]').get_attribute("innerHTML")
       
        try:
            message = review.find_element(By.CSS_SELECTOR, '[class="review-text-container___2NHwE"]').get_attribute("innerHTML")
        except:
            try:
                message = review.find_element(By.CSS_SELECTOR, '[class="clamped___1_0yP gl-vspace gl-body gl-no-\
                margin-bottom"]').get_attribute("innerHTML")
            except:
                message = None

        try:
            review_info = review.find_element(By.CSS_SELECTOR, '[class="info___PBHlc gl-vspace"]').get_attribute("innerHTML")
        except:
            review_info = None

        heading.append(header)
        messaging.append(message)
        info.append(review_info)
        
        driver.close()
        
    return heading, messaging, info





def wrangle_adidas_data(data):
    '''-Helps to clean the info column to get more precise column
            - input: data to be wrangled
            - Returns: the wrangled data
    '''
    
    data = data.copy()
    data.ReviewInfo.fillna("No Info", inplace=True)
   
    users = []
    dates = []
    verifys = []
    reviews= []

    for dat in data["ReviewInfo"]:
        if dat is not "No Info":
            #iterate through on several conditions
            if dat is not None:
                dat_split = dat.split("|")
                if len(dat_split) >= 4:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    verifys.append(True)
                    reviews.append(True)
                elif len(dat_split) == 3:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    if dat_split[2] == ' Verified Purchaser ':
                        verifys.append(True)
                        reviews.append(False)
                    else:
                        verifys.append(False)
                        reviews.append(True)
                else:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    verifys.append(False)
                    reviews.append(False)

            else:
                users.append(None)
                dates.append(None)
                verifys.append(False)
                reviews.append(False)
        else:
            users.append(None)
            dates.append(None)
            verifys.append(False)
            reviews.append(False)
            

    data["UserID"] = users 
    data["Date"] = dates
    data["VerifiedPurchaser"] = verifys
    data["IncentivizedReview"] = reviews

    data.drop(columns="ReviewInfo", inplace=True)
    data["Price"].astype(int)
    data["ColoursAvailable"].astype(int)
    data.UserID.fillna("Unknown", inplace=True)
    data.Reviews.fillna("No Topic", inplace=True)
    
    return data

df = wrangle_adidas_data(df)