import requests
import json
import pandas as pd
import re
import spacy
import pickle
pd.set_option("display.max_columns", None)
import os
from selenium import webdriver
from  selenium.webdriver.common.by import By
from  selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

os.environ["PATH"] += r"C:/SeleniumDrivers"
import math as mt

def fetch_reviews(product_number):
    """
    The function fetches users comment from nike.com
    -Arguments:
        product_number: This selects the product number on the search_list

    -Returns:
        Customer Reviews
    """
    
    url = "https://www.nike.com"
    driver = webdriver.Chrome()
    driver.get(url=url)
    driver.maximize_window()
    driver.implicitly_wait(15)


    #click the terms and conditions button
    try:
        confirm_button = driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='Accept All']")
        confirm_button.click()
    except:
        print(f"No confirm button")

    #click the geomix match dismiss button
    try:
        button = driver.find_element(By.CSS_SELECTOR, 'button[data-type="click_geoMismatchDismiss"]')
        button.click()
    except:
         print("Geo-dismiss button didn't pop up")

    search = driver.find_element(by=By.ID, value="VisualSearchInput")
    search.send_keys("shoe")
    search.send_keys(Keys.ENTER)

    #click the terms and conditions button
    try:
        confirm_button = driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='Accept All']")
        confirm_button.click()
    except:
        print(f"No confirm button")

    #click possible pop up button
    try:
        close_button = driver.find_elements(by=By.CSS_SELECTOR, value="button[data-var= 'closeButton']")
        close_button.click()
    except:
        print("No pop up icon to close")

    #click the geomix match dismiss button
    try:
        button = driver.find_element(By.CSS_SELECTOR, 'button[data-type="click_geoMismatchDismiss"]')
        button.click()
    except:
         print("Geo-dismiss button didn't pop up")
            
    xpath = f'//*[@id="skip-to-products"]/div[{product_number}]'
    product = driver.find_element(By.XPATH, xpath)
    product.click()

    review_button_element = driver.find_element(By.CSS_SELECTOR, '[data-test="reviewsAccordionClick"]')
    review_button_element.click()

    more_review_button_element = driver.find_element(By.CSS_SELECTOR,'[for="More Reviews"]')
    more_review_button_element.click()

    count = int(driver.find_element(by=By.CSS_SELECTOR,
                                value='[aria-level="2"]'
                               ).get_attribute("innerText")[:2])

    content = []

    for i  in range(mt.ceil(count/16)):

        review_element  = driver.find_element(By.ID, "tt-reviews-list")
        reviews = review_element.find_elements(By.CLASS_NAME, "tt-c-review")

        for review in reviews:
            try:
                inner = review.get_attribute("innerText")
                outer = review.get_attribute("OuterText")
                content.append([inner, outer])
            except:
                content.append(["Null", "Null"])

            more_review_button_element2 = driver.find_element(By.CSS_SELECTOR,'[aria-label="Go to next reviews"]')
            more_review_button_element2.click()
            
    return len(content), content


def clean_review(review):
    review = review.replace('How did this product fit?:Runs Small\nHow comfortable was this product?:Very Comfortable\n', '')
    review = re.sub(r'Read More\n.*$', '', review)
    return review.strip()


def clean_reviews(data):
    df = data.copy()

    clean_review = []
    promo = []

    for rev, username in zip(df.Review.values, df.Username.values):

        promo_message = "[This review was collected as part of a promotion.]"
        review_sub_str = "How did this product fit"
        rating1, rating2, rating3, rating4, rating5 = "1 out of 5\n", "2 out of 5\n",\
            "3 out of 5\n", "4 out of 5\n", "5 out of 5\n"
        new_rev = str(rev)
        username = str(username)
        promo_review = False
        
        try:
            
            if username in new_rev:
                username_index = rev.find(username)
                rev = rev[:username_index-2]

                if (rating1 or rating2 or rating3 or rating4 or rating5) in rev:
                    rev = rev[11:]
                    new_rev = rev
                    if promo_message in rev:
                        new_rev = rev.replace(promo_message, "")
                        promo_review = True

                    elif review_sub_str in rev:
                        promo_review = False
                        if "Yes" in rev:
                            if "True to Size" in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:Yes\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Average\nWould you recommend this product?:Yes\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:Yes\n","")
                            elif 'Runs Big' in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:Yes\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Average\nWould you recommend this product?:Yes\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:Yes\n","")
                            elif 'Runs Small' in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:Yes\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Average\nWould you recommend this product?:Yes\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:Yes\n","")

                        elif "No" in rev:
                            if "True to Size" in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:No\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Average\nWould you recommend this product?:No\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:True to Size\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:No\n","")
                            elif 'Runs Big' in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:No\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Average\nWould you recommend this product?:No\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Big\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:No\n","")
                            elif 'Runs Small' in rev:
                                if 'Very Comfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Very Comfortable\nWould you recommend this product?:No\n", "")
                                elif 'Average' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Average\nWould you recommend this product?:No\n", "","")
                                elif 'Uncomfortable' in rev:
                                    new_rev = rev.replace("How did this product fit?:Runs Small\nHow comfortable was this product?:Uncomfortable\nWould you recommend this product?:No\n","")
                   
        except:
            promo_review = False
            new_rev = rev
            
        clean_review.append(new_rev)
        promo.append(promo_review)
        
        
    print(len(clean_review))
    print(len(promo))

    df["Review"] =  clean_review
    df["IsPromoReview"] =  promo
    return df


def import_from_nike_api(search="shoe", anchor=0, count=60):
    
    url = f"https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=381580E0BF3EB5876C338BF0368C04A7&\
    country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)\
    %26filter%3DemployeePrice(true)%26searchTerms%3D{search}%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-\
    f159cf99c647%26count%3D{count}&language=en&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"

    html = requests.get(url)
    output = json.loads(html.text)
    products = output["data"]["products"]["products"]
    
    def extract_nested_dicts(d):
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            nested_dict = extract_nested_dicts(v)
            new_dict.update(nested_dict)
        elif isinstance(v, list):
            new_dict[k] = [extract_nested_dicts(item) if isinstance(item, dict) else item for item in v]
        else:
            new_dict[k] = v
    return new_dict


