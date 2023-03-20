from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin 
import re

#important note : every single class element must be monitored periodically, because they can be changed anytime, soo keep inspecting the element enytime you want to scrap

link = "https://www.google.com/maps/search/Restaurants/@-6.116773,106.7607085,13z/data=!3m1!4b1"

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

e = []
le = 0

def Selenium_extractor():
    matriks = []
    action = ActionChains(browser)
    a = browser.find_elements(By.CLASS_NAME, "hfpxzc")

    while len(a) < 1000:
        #print(len(a))
        var = len(a)
        scroll_origin = ScrollOrigin.from_element(a[len(a)-1])
        action.scroll_from_origin(scroll_origin, 0, 1000).perform()
        time.sleep(2)
        a = browser.find_elements(By.CLASS_NAME, "hfpxzc")#always keep your eyes on the class (hfpxzc) it can be changed anytime
        #print(a)
        if len(a) == var:
            le+=1
            if le > 20:
                break
        else:
            le = 0

    for i in range(len(a)):
        scroll_origin = ScrollOrigin.from_element(a[i])
        action.scroll_from_origin(scroll_origin, 0, 100).perform()
        action.move_to_element(a[i]).perform()
        a[i].click()
        time.sleep(2)
        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        detail = soup.findAll("div", {"class" : "UaQhfb fontBodyMedium"})
        #b = soup.findAll("div", {"class" : "AeaXub"})
        c = soup.findAll("div", {"class" : "m6QErb WNBkOb"})
        alamt = soup.findAll("div", {"class" : "AeaXub"})
        
        nama_resto = soup.find("h1" , {"class" : "DUwDvf fontHeadlineLarge"})
        #name = nama_resto.text

        address_elements = browser.find_elements(By.CSS_SELECTOR,"[data-item-id='address']")
        addresses = [element.get_attribute("innerHTML") for element in address_elements]
        addresses = [address.get_text() for address in soup.select("[data-item-id='address']")]
        
        no_telp_element = browser.find_elements(By.CSS_SELECTOR,"[data-tooltip='Salin nomor telepon']")
        no_telp = [elements.get_attribute("innerHTML") for elements in no_telp_element]
        no_telp = [number.get_text() for number in soup.select("[data-tooltip='Salin nomor telepon']")]
        
        location_detail_html = browser.find_elements(By.CSS_SELECTOR,"[data-item-id='oloc']")
        location_detail = [elements.get_attribute("innerHTML") for elements in location_detail_html]
        location_detail = [loc.get_text() for loc in soup.select("[data-item-id='oloc']")]
        #print(location_detail)
        
        website_element = browser.find_elements(By.CSS_SELECTOR,"[data-item-id='authority']")
        website = [elements.get_attribute("innerHTML") for elements in website_element]
        website = [web.get_text() for web in soup.select("[data-item-id='authority']")]
        
        review_html = soup.find("button" , {"class" : "HHrUdb fontTitleSmall rqjGif"})
        if review_html is not None :
            reviews=review_html.text
        
        star_html = soup.find("div", {"class" : "fontDisplayLarge"})
        if star_html is not None :
            star = star_html.text
            star = star.replace(",", ".")
        
        resto_type_html = soup.find("button" , {"class" : "DkEaL u6ijk"})
        
        price_level_html = soup.find("span" , {"class" : "mgr77e"})
        if price_level_html is not None :
            price_level=price_level_html.text
            if price_level == "·$":
                price_level= 1
            if price_level == "·$$":
                price_level= 2
            if price_level == "·$$$":
                price_level= 3
            if price_level == "·$$$$":
                price_level= 4
        if price_level_html is None:
            price_level= "NaN"
        
        if nama_resto is not None and addresses is not None and no_telp is not None and resto_type_html is not None :
            data = {"resto" : nama_resto.text, "alamat" : addresses, "location" : location_detail, 
                    "Phone" : no_telp, "website" : website, "star": star ,
                    "reviews" : reviews, "priceLevel" : price_level, "restoType" : resto_type_html.text}
            print(data)
            
browser.get(str(link))
time.sleep(10)
Selenium_extractor()
       
