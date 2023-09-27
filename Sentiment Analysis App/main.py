import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

os.environ["PATH"] += r"C:/SeleniumDrivers"

driver_chrome = webdriver.Chrome()
#driver_edge = webdriver.Edge()
driver_chrome.implicitly_wait(3)

url = "https://www.nike.com/t/ajko-1-low-mens-shoes-HNz9ps/DX4981-006"
driver_chrome.get(url=url)

#agree_button = driver_chrome.find_element(By.CSS_SELECTOR, "button[aria-label = 'Confirm Choices']")
#agree_button.click()

#close_button = driver_chrome.find_element(By.CSS_SELECTOR, "button[data-var = 'closeButton']")
#close_button.click()

#comment = driver_chrome.find_elements(By.CSS_SELECTOR, "span.tt-c-review__text-content")
comment = driver_chrome.find_elements(By.XPATH, "//span[@class='tt-c-review__text-content']")

print(comment)
#driver_edge.get(url=url)

