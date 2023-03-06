from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin 
import re


filename = "data"
link = "https://www.google.com/maps/search/Restaurants/@-6.116591,106.6906678,12z/data=!4m2!2m1!6e5"

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#options.add_argument("--headless")
browser = webdriver.Chrome(options=options)

record = []
new_list= []

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

        for element in detail:
            content=element.text
            matriks.append(content)
        
            
            #print(record)
            #print(matriks)

            new_list = []
            for item in matriks:
                match = re.match(r'(.*?)\s+([\d,\.]+)\((\d+)\)\s+·\s*(.*?)\s*·\s*(.*?)\s*·\s*(.*?)\s*', item)
            if match:
                groups = match.groups()
                if '$$$$' or '$$$' or '$$' not in  groups[3]:
                    groups = list(groups)
                    groups[3] = '-'
                    new_item = ' '.join(groups)
                    new_list.append(new_item)
            else:
                new_list.append(item)

            if new_list != []:
                print(new_list)
            
browser.get(str(link))
time.sleep(10)
Selenium_extractor()

"""
for d in matriks:
                    # Buang karakter whitespace di awal dan akhir
                d = d.strip()
                 # Pisahkan data menjadi beberapa bagian dengan karakter pemisah "·"
                parts = d.split("·")
                    # Ambil nilai-nilai yang sesuai untuk setiap kolom yang diinginkan
                restaurant = parts[0].split("    ")[0].split("(")[0].split(")")[0].strip()
                rating= (parts[0].split("         ")[1].split("(")[0].split(")")[0].replace(",", "."))
                jumlah_review = (parts[0].split("(")[0].split(")")[0])
                category = (parts[1].split("(")[0].split(")")[0])
                address = parts[2].strip()
                type_ = parts[3].strip()
                #description = parts[4].strip()
                details = {"nama_restaurant" : restaurant, "Ratings" : rating, "jumlah_review" : jumlah_review, \
                    "category" : category, "alamat" : address, "tipe" : type_ }
                record.append(details)
"""