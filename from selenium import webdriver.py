from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin 
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import time
import re
import json
import pymongo 
import bson.json_util as json_util
import logging
import os

#Tutup sementara

"""from pyvirtualdisplay import Display

# Inisialisasi dan konfigurasi virtual display
display = Display(visible=0, size=(800, 600))
display.start()"""


#-6.116773,106.7607085

def insert_new_data(data):
    # get data from database
    client = pymongo.MongoClient('your_mongodb_database_client')
    db = client["your_db_name"]
    collection = db["your_collection"]
    toDb = dict(data)
     #checking the availibility of certain data
    existing_doc = collection.find_one({'url': toDb['url']})

    if existing_doc is None:
        try :
            collection.insert_one(toDb)
            logging.info('Data transferred successfully')
            print('New Document has been inserted.')
        except Exception as e :
            logging.error(f'Error transferring data: {e}')
    else:
        try :
            logging.info('Document is already existed')
            print('Document is already existed.')
        except Exception as e :
            logging.error(f'Error connecting to db {e}')

def SeleniumExtractor(tenant, search_location):
    link = f"www.google.com"
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    link = "https://www.google.com/maps/"
    browser.get(str(link))
    time.sleep(5)

    search_box = browser.find_element(By.ID,"searchboxinput")
    search_box.send_keys(search_location)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)
    
    # get lat long and change the z value
    url_lat_long = browser.current_url
    url_lat_long = url_lat_long.split('/')
    lat_long = url_lat_long[6]
    lat_long = lat_long.split(',')
    new_lat_long = lat_long[0]+','+lat_long[1]+','+'14z'

    # search restaurant add ?hl=en for language default to english
    link = "https://www.google.com/maps/search/{}/{}".format(tenant,new_lat_long)
    browser.get(str(link))
    time.sleep(5)

    feed_element = browser.find_element(By.XPATH,"//div[@role='feed']")
    print('get all tenant possible')
    
    # Scroll x times -> increase range get more scroll action, list available is depend on google maps itself
    for num in range(1,1):
       browser.execute_script("arguments[0].scroll(0, arguments[0].scrollHeight);", feed_element)
       time.sleep(5) # wait time until the list is shown, it will depends on network

    list_all = []
    gofood_list = []
    elements = feed_element.find_elements(By.XPATH,"//div[@role='article']")
    for i in elements:
        tenantName = (i.get_attribute("aria-label"))

        try:
            rating = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[3]/div/span[2]/span/span[1]").text
        except:
            rating = None
        
        try:
            rating_total = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[3]/div/span[2]/span/span[2]").text
        except:
            rating_total = None

        try:
            price_level = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[3]/div/span[3]/span[2]").text
            #price_level = price_level_.find_element(By.XPATH,"//span[@role='img']").text
        except:
            price_level = None
        
        try:
            merchant_type = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[4]/div[1]/span[1]").text
        except:
            merchant_type = None
        
        try:
            address = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[4]/div[1]/span[2]/span[2]").text
        except:
            address = None
        
        try:
            url = i.find_element(By.XPATH,"a").get_attribute("href")
        except:
            url = None

        try :
            pattern = r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"
            match = re.search(pattern, url)
            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                geometry = (latitude, longitude)
        except :
            geometry = None

        try :
            business_status = i.find_element(By.XPATH,"div/div[4]/div[1]/div/div/div[2]/div[4]/div[2]/span/span/span").text
        except :
            business_status = None
        
        result = {
            "tenantType": "Pub",
            "tenantName": tenantName,
            "merchantType" : merchant_type,
            "rating": rating,
            "rating_total": rating_total,
            "priceLevel" : price_level,
            "tenantAddress": address,
            "businessStatus" : business_status,
            "url": url,
            "geometry" : geometry,
            "details": {},
            "createdAt" : datetime.now().isoformat(),
            "updatedAt" : None, 
            "createdBy" : "System", 
            "updatedBy" : None, 
            "crawlId" : "63f22112d43f15a207941e58"
        }
        list_all.append(result)

    count_all_tenants = len(list_all)
    print("get {} tenants".format(count_all_tenants))

    # in this line the list_all should be filled up so we iterate once more to obtain the details
    row_ = 1
    for item in list_all:
        browser.get(str(item['url']))
        print('get detail {} of {} | {}'.format(row_, count_all_tenants, item['tenantName']))
        time.sleep(5)

        # Overview Tab
        overview_tab = browser.find_element(By.XPATH,"//div[@role='region']")

        try:
            desc = i.find_element(By.XPATH,"div[2]/div/div/div[2]").text
        except:
            desc = None
        
        try:
            full_address = overview_tab.find_element(By.XPATH,"//button[@data-item-id='address']").get_attribute("aria-label")
            full_address = re.sub('Address: ','',full_address)
        except:
            full_address = None

        try:
            plus_code = overview_tab.find_element(By.XPATH,"//button[@data-item-id='oloc']").get_attribute("aria-label")
        except:
            plus_code=None

        try:
            schedule = overview_tab.find_element(By.XPATH,"//div[contains(@aria-label,'jam buka')]").get_attribute("aria-label")
            schedule =schedule.split("Sembunyikan jam buka untuk seminggu")
            schedule =schedule[0].split(";")
            schedule = [s.replace(",Jam buka dapat berbeda", "") for s in schedule]
            schedule = [s.replace(" hingga ", "-") for s in schedule]
            schedule_dict = []
            for s in schedule:
                day, hours = s.split(",")
                day = day.lower()
                schedule_dict.append({"hari": day, "jam_buka": hours})

            schedule_dict = {"periods": []}
            for s in schedule:
                day, hours = s.split(",")
                day = day.lower()
                day_num = day.replace("senin", "1").replace("selasa", "2").replace("rabu", "3").replace("kamis", "4").replace("jumat", "5").replace("sabtu", "6").replace("minggu", "0")
                buka, tutup = hours.split("-")
                day_dict = {"hari" : day_num.strip(), "buka": buka, "tutup": tutup}
                schedule_dict["periods"].append(day_dict)

        except:
            schedule_dict = None
        
        try:
            located_in = overview_tab.find_element(By.XPATH,"//button[@data-item-id='locatedin']").get_attribute("aria-label")
            located_in = re.sub('Located in: ','',located_in)
        except:
            located_in = None

        try:
            phone = overview_tab.find_element(By.XPATH,"//button[@data-tooltip='Salin nomor telepon']").get_attribute("aria-label")
            phone = re.sub('\D','',phone)
        except:
            phone = None

        try:
            website = overview_tab.find_element(By.XPATH,"//a[@data-item-id='authority']").get_attribute("href")
        except:
            website = None

        try :
            main_element = browser.find_element("xpath","//div[@role='region']")
            elements = main_element.find_elements("xpath","//div[@role='img']")
            popular_time = [element.get_attribute("aria-label") for element in elements]
            
            #data minggu
            minggu = popular_time[0:18]
            for i in range(len(minggu)):
                if "Saat ini" in minggu[i]:
                    now = datetime.now().strftime("%H.%M")
                    minggu[i] = minggu[i].replace("Saat ini", "pukul " + now)
                    
            #data senin
            senin= popular_time[18:36]
            for i in range(len(senin)):
                if "Saat ini" in senin[i]:
                    now = datetime.now().strftime("%H.%M")
                    senin[i] = senin[i].replace("Saat ini", "pukul " + now)
                    
            #data selasa
            selasa = popular_time[36:54]
            for i in range(len(selasa)):
                if "Saat ini" in selasa[i]:
                    now = datetime.now().strftime("%H.%M")
                    selasa[i] = selasa[i].replace("Saat ini", "pukul " + now)
                    
            #data rabu
            rabu = popular_time[54:72]
            for i in range(len(rabu)):
                if "Saat ini" in rabu[i]:
                    now = datetime.now().strftime("%H.%M")
                    rabu[i] = rabu[i].replace("Saat ini", "pukul " + now)
                    
            #data kamis
            kamis = popular_time[72:90]
            for i in range(len(kamis)):
                if "Saat ini" in kamis[i]:
                    now = datetime.now().strftime("%H.%M")
                    kamis[i] = kamis[i].replace("Saat ini", "pukul " + now)
                    
            #jumat
            jumat = popular_time[90:108]
            for i in range(len(jumat)):
                if "Saat ini" in jumat[i]:
                    now = datetime.now().strftime("%H.%M")
                    jumat[i] = jumat[i].replace("Saat ini", "pukul " + now)
                    
            #data sabtu
            sabtu = popular_time[108:126]
            for i in range(len(sabtu)):
                if "Saat ini" in sabtu[i]:
                    now = datetime.now().strftime("%H.%M")
                    sabtu[i] = sabtu[i].replace("Saat ini", "pukul " + now)
            
            #minggu
            jam_minggu = []  
            for d in minggu:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_minggu.append(m.group(1))
            

            value_minggu = []
            for d in minggu:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_minggu.append(m.group(1))
            value_minggu = [int(x) for x in value_minggu]   

            #senin
            jam_senin = []  
            for d in senin:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_senin.append(m.group(1))
                    
            value_senin = []
            for d in senin:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_senin.append(m.group(1))
            value_senin = [int(x) for x in value_senin] 

            #selasa
            jam_selasa = []  
            for d in selasa:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_selasa.append(m.group(1))
                    
            value_selasa = []
            for d in selasa:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_selasa.append(m.group(1))
            value_selasa = [int(x) for x in value_selasa]      

            #rabu
            jam_rabu = []  
            for d in rabu:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_rabu.append(m.group(1))
                    
            value_rabu = []
            for d in rabu:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_rabu.append(m.group(1))
            value_rabu = [int(x) for x in value_rabu] 

            #kamis
            jam_kamis = []  
            for d in kamis:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_kamis.append(m.group(1))
                    
            value_kamis = []
            for d in kamis:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_kamis.append(m.group(1))
            value_kamis = [int(x) for x in value_kamis] 

            #jumat
            jam_jumat = []  
            for d in jumat:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_jumat.append(m.group(1))
                    
            value_jumat = []
            for d in jumat:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_jumat.append(m.group(1))
            value_jumat = [int(x) for x in value_jumat]     

            #sabtu
            jam_sabtu = []  
            for d in sabtu:
                m = re.search(r'(\d{2}\.\d{2})', d)
                if m:
                    jam_sabtu.append(m.group(1))
                    
            value_sabtu = []
            for d in sabtu:
                m = re.search(r'\b(\d+)%', d)
                if m:
                    value_sabtu.append(m.group(1))
            value_sabtu = [int(x) for x in value_sabtu] 

            detail_hours = [{"day" : "minggu", "detailHours" :jam_minggu , "detailValue" : value_minggu},
                            {"day" : "senin", "detailHours" :jam_senin , "detailValue" : value_senin},
                            {"day" : "selasa", "detailHours" :jam_selasa , "detailValue" : value_selasa}, 
                            {"day" : "rabu", "detailHours" :jam_rabu , "detailValue" : value_rabu},
                            {"day" : "kamis", "detailHours" :jam_kamis , "detailValue" : value_kamis},
                            {"day" : "jumat", "detailHours" :jam_jumat , "detailValue" : value_jumat}, 
                            {"day" : "sabtu", "detailHours" :jam_sabtu , "detailValue" : value_sabtu}]
            
            popular_times = {"updateDate" : datetime.now().strftime("%m-%d-%Y"), "detail" : detail_hours}
            
        except :
            popular_times = None      
        
        photo_url=[]
        try :
            photos_element = browser.find_element(By.XPATH,"//div[contains(@aria-label,'Foto')]")
            try :
                photo1 = photos_element.find_element(By.XPATH,"div/div[2]/button[1]/img")
                photo_1_url = photo1.get_attribute("src")
                photo_url.append(photo_1_url)
            except :
                photo_1_url = None
                photo_url.append(photo_1_url)
                
            try :
                photo2 = photos_element.find_element(By.XPATH,"div/div[2]/button[2]/img")
                photo_2_url = photo2.get_attribute("src")
                photo_url.append(photo_2_url)
            except :
                photo_2_url = None
                photo_url.append(photo_2_url)
                
            try :
                photo3 = photos_element.find_element(By.XPATH,"div/div[2]/button[3]/img")
                photo_3_url = photo3.get_attribute("src")
                photo_url.append(photo_3_url)
            except :
                photo_3_url = None
                photo_url.append(photo_3_url)
                
            try :
                photo4 = photos_element.find_element(By.XPATH,"div/div[2]/button[4]/img")
                photo_4_url = photo4.get_attribute("src")
                photo_url.append(photo_4_url)
            except :
                photo_4_url = None
                photo_url.append(photo_4_url)
                
            try :
                photo5 = photos_element.find_element(By.XPATH,"div/div[2]/button[5]/img")
                photo_5_url = photo5.get_attribute("src")
                photo_url.append(photo_5_url)
            except :
                photo_5_url = None
                photo_url.append(photo_5_url)
                
            try :
                photo6 = photos_element.find_element(By.XPATH,"div/div[2]/button[6]/img")
                photo_6_url = photo6.get_attribute("src")
                photo_url.append(photo_6_url)
            except :
                photo_6_url = None
                photo_url.append(photo_6_url)
                
            try :
                photo7 = photos_element.find_element(By.XPATH,"div/div[2]/button[7]/img")
                photo_7_url = photo7.get_attribute("src")
                photo_url.append(photo_7_url)
            except :
                photo_7_url = None
                photo_url.append(photo_7_url)
                
            try :
                photo8 = photos_element.find_element(By.XPATH,"div/div[2]/button[8]/img")
                photo_8_url = photo8.get_attribute("src")
                photo_url.append(photo_8_url)
            except :
                photo_8_url = None
                photo_url.append(photo_8_url)
                
            try :
                photo9 = photos_element.find_element(By.XPATH,"div/div[2]/button[9]/img")
                photo_9_url = photo9.get_attribute("src")
                photo_url.append(photo_9_url)
            except :
                photo_9_url = None
                photo_url.append(photo_9_url)
                
            try :
                photo10 = photos_element.find_element(By.XPATH,"div/div[2]/button[10]/img")
                photo_10_url = photo10.get_attribute("src")
                photo_url.append(photo_10_url)
            except :
                photo_10_url = None
                photo_url.append(photo_10_url)
                
            try :
                photo11 = photos_element.find_element(By.XPATH,"div/div[2]/button[11]/img")
                photo_11_url = photo11.get_attribute("src")
                photo_url.append(photo_11_url)
            except :
                photo_11_url = None
                photo_url.append(photo_11_url)
                
            try :
                photo12 = photos_element.find_element(By.XPATH,"div/div[2]/button[12]/img")
                photo_12_url = photo12.get_attribute("src")
                photo_url.append(photo_12_url)
            except :
                photo_12_url = None
                photo_url.append(photo_12_url)
            
            try :
                photo13 = photos_element.find_element(By.XPATH,"div/div[2]/button[13]/img")
                photo_13_url = photo13.get_attribute("src")
                photo_url.append(photo_13_url)
            except :
                photo_13_url = None
                photo_url.append(photo_13_url)
                
            try :
                photo14 = photos_element.find_element(By.XPATH,"div/div[2]/button[14]/img")
                photo_14_url = photo14.get_attribute("src")
                photo_url.append(photo_14_url)
            except :
                photo_14_url = None
                photo_url.append(photo_14_url)
            
            try :
                photo15 = photos_element.find_element(By.XPATH,"div/div[2]/button[15]/img")
                photo_15_url = photo15.get_attribute("src")
                photo_url.append(photo_15_url)
            except :
                photo_15_url = None
                photo_url.append(photo_15_url)
            
            try :
                photo16 = photos_element.find_element(By.XPATH,"div/div[2]/button[16]/img")
                photo_16_url = photo16.get_attribute("src")
                photo_url.append(photo_16_url)
            except :
                photo_16_url = None
                photo_url.append(photo_16_url)
            
            try :
                photo17 = photos_element.find_element(By.XPATH,"div/div[2]/button[17]/img")
                photo_17_url = photo17.get_attribute("src")
                photo_url.append(photo_17_url)
            except :
                photo_17_url = None
                photo_url.append(photo_17_url)
                
            try :
                photo18 = photos_element.find_element(By.XPATH,"div/div[2]/button[18]/img")
                photo_18_url = photo18.get_attribute("src")
                photo_url.append(photo_18_url)
            except :
                photo_18_url = None
                photo_url.append(photo_18_url)
            
            try :
                photo19 = photos_element.find_element(By.XPATH,"div/div[2]/button[19]/img")
                photo_19_url = photo19.get_attribute("src")
                photo_url.append(photo_19_url)
            except :
                photo_19_url = None
                photo_url.append(photo_19_url)
                
            try :
                photo20 = photos_element.find_element(By.XPATH,"div/div[2]/button[20]/img")
                photo_20_url = photo20.get_attribute("src")
                photo_url.append(photo_20_url)
            except :
                photo_20_url = None
                photo_url.append(photo_20_url)
                
        except :   
            photo_1_url = None
            photo_2_url = None
            photo_3_url = None
            photo_4_url = None
            photo_5_url = None
            photo_6_url = None
            photo_7_url = None
            photo_8_url = None
            photo_9_url = None
            photo_10_url = None
            photo_11_url = None
            photo_12_url = None
            photo_13_url = None
            photo_14_url = None
            photo_15_url = None
            photo_16_url = None
            photo_17_url = None
            photo_18_url = None
            photo_19_url = None
            photo_20_url = None
        try : 
            kode_pos = re.findall(r'\b\d{5}\b', full_address)[0]
        except :
            kode_pos = None

        district = " "
        try :
            posisi_kec = full_address.find("Kec.")
            posisi_koma = full_address.find(",", posisi_kec)
            posisi_kecamatan = full_address.find("Kecamatan")
            posisi_koma_kecamatan = full_address.find(",", posisi_kecamatan)
            if posisi_kec != -1:
                district = full_address[posisi_kec + len("Kec."):posisi_koma].strip()
            elif posisi_kecamatan != -1:
                district = full_address[posisi_kecamatan + len("Kecamatan"):posisi_koma_kecamatan].strip()

        except : 
            district = None
        try : 
            split_location = plus_code.split(", ")
            try :
                city = split_location[1]
            except :
                city = None
            try :
                province = split_location[2]
            except :
                province = None
            try :
                if "Kabupaten" in city :
                    city= city.replace("Kabupaten", " ")
            except :
                city = None

        except :
            split_location = None

        try : 
            driver = webdriver.Chrome()
            driver.get("https://www.bing.com/")
            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(f"gofood.co.id-{item['tenantName']}-{district}") 
            time.sleep(5)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            website_link = driver.find_element(By.PARTIAL_LINK_TEXT, "gofood.co.id")  
            time.sleep(7)
            website_link.click()
            time.sleep(3)

            try:
                url = driver.find_element(By.XPATH,"//link[@hreflang='id']").get_attribute("href")
            except:
                url = None

            feed_elements = driver.find_elements(By.XPATH, "//div[@id='__next']")  # Menggunakan elements (plural)

            for element in feed_elements:  # Menggunakan feed_elements (plural)
                # ...
                # Bagian pengambilan data lainnya
                # ...
                try :
                    name = element.find_element(By.XPATH, "div/div[2]/div[1]/div[1]/div[1]/div[1]/h1").text
                except :
                    name = None

                try :
                    alamat = element.find_element(By.XPATH, "div/div[2]/div[1]/div[1]/div[1]/div[3]/p").text
                except :
                    alamat = None

                try :
                    rating = element.find_element(By.XPATH, "div/div[2]/div[1]/div[2]/div/div[1]/div/p").text
                except :
                    rating = None

                price_level=[]
                price_lvl = ""
                try :
                    price_level1 = element.find_element(By.XPATH, "div/div[2]/div[1]/div[2]/div/div[3]/div/div[1]/div[1]").get_attribute("class")
                    price_level2 = element.find_element(By.XPATH, "div/div[2]/div[1]/div[2]/div/div[3]/div/div[1]/div[2]").get_attribute("class")
                    price_level3 = element.find_element(By.XPATH, "div/div[2]/div[1]/div[2]/div/div[3]/div/div[1]/div[3]").get_attribute("class")
                    price_level4 = element.find_element(By.XPATH, "div/div[2]/div[1]/div[2]/div/div[3]/div/div[1]/div[4]").get_attribute("class")
                    
                    if price_level1== "text-gf-content-primary":
                        price_level.append(price_level1) 

                    if price_level2== "text-gf-content-primary":
                        price_level.append(price_level2) 

                    if price_level3== "text-gf-content-primary":
                        price_level.append(price_level3) 

                    if price_level4== "text-gf-content-primary":
                        price_level.append(price_level4) 

                    price_lvl = len(price_level)

                except :
                    price_level = None
                    price_lvl = price_level
                try:
                    ulasan = element.find_element(By.XPATH,"div/div[2]/div[2]/div/button[2]")
                    time.sleep(3)
                    ulasan.click()
                    time.sleep(3)

                    ulasan_detail = element.find_elements(By.XPATH,"div/div[2]/div[3]/div/div[2]")
                    reviewer = ""
                    review_rating = ""
                    text_review =""
                    for i in ulasan_detail:
                        reviewer = i.find_element(By.XPATH, "div/div[1]/div[2]/h3").text
                        review_rating = i.find_element(By.XPATH, "div/div[1]/div[3]/div/span").text
                        text_review = i.find_element(By.XPATH, "div/div[2]/div/p").text
                    
                except :
                    reviewer = None
                    review_rating = None
                    text_review =None
                gofood = {
                    "url": url,
                    "name": name,
                    "alamat": alamat,
                    "rating": rating,
                    "price level": price_lvl,
                    "reviews": {
                        "reviewerName": reviewer,
                        "ratings": review_rating,
                        "text": text_review
                    }
                }

                gofood_list.append(gofood)

        except :
            gofood_list = None     
        # Move to reviews tab, sort by newest
        tablist_detail = browser.find_elements(By.XPATH,"//div[@role='tablist']/button[@role='tab']")
        
        button_review = list(tablist_detail)[1]
        button_review.click()
        time.sleep(5)
        
        try :
            button_sort = browser.find_element(By.XPATH,"//button[@data-value='Urutkan']")
            button_sort.click()
            time.sleep(0.5)

            choices = browser.find_elements(By.XPATH,"//div[@id='action-menu']/div[@role='menuitemradio']")

            newest_choices = list(choices)[1]
            newest_choices.click()
            time.sleep(2)

        # Scroll x times -> increase range get more scroll action, list available is depend on google maps itself
            scrollable_review = browser.find_element(By.XPATH,"//div[@role='main']/div[3]")
            for num in range(1,10):
                browser.execute_script("arguments[0].scroll(0, arguments[0].scrollHeight);", scrollable_review)
                time.sleep(2) # wait time until the list is shown, it will depends on network

            main_element = browser.find_element(By.XPATH,"//div[@role='main']")

        # Reviews Tab
            reviews = []
            list_reviews_element = list(main_element.find_elements(By.XPATH,"div[3]/div"))[-2].find_elements(By.XPATH,"div")

            for review_detail in list_reviews_element:
                try:
                    review_id = review_detail.get_attribute("data-review-id")
                except:
                    review_id = None
            
                try:
                    reviewer_name = review_detail.get_attribute("aria-label")
                except:
                    reviewer_name = None

                try:
                    #review_str = review_detail.find_element(By.XPATH,"div/div/div[4]/div[1]/span[1]").get_attribute("aria-label")
                    review_star1 = review_detail.find_element(By.XPATH, "div/div/div[4]/div[1]/span[1]/img[1]").get_attribute("src")
                    review_star2 = review_detail.find_element(By.XPATH, "div/div/div[4]/div[1]/span[1]/img[2]").get_attribute("src")
                    review_star3 = review_detail.find_element(By.XPATH, "div/div/div[4]/div[1]/span[1]/img[3]").get_attribute("src")
                    review_star4 = review_detail.find_element(By.XPATH, "div/div/div[4]/div[1]/span[1]/img[4]").get_attribute("src")
                    review_star5 = review_detail.find_element(By.XPATH, "div/div/div[4]/div[1]/span[1]/img[5]").get_attribute("src")
                    
                    review_list = []
                    if review_star1 == "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png":
                        review_list.append(review_star1)

                    if review_star2 == "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png":
                        review_list.append(review_star2)

                    if review_star3 == "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png":
                        review_list.append(review_star3)
    
                    if review_star4 == "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png":
                        review_list.append(review_star4)
    
                    if review_star5 == "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png":
                        review_list.append(review_star5)

                    review_star = len(review_list)
                except:
                    review_star = None
                
                try:
                    review_time = review_detail.find_element(By.XPATH,"div/div/div[4]/div[1]/span[2]").text
                    waktu_hari_ini = datetime.now() - timedelta(days=0)
                    waktu_sehari_lalu = datetime.now() - timedelta(days=1)
                    waktu_duahari_lalu = datetime.now() - timedelta(days=2)
                    waktu_tigahari_lalu = datetime.now() - timedelta(days=3)
                    waktu_empathari_lalu = datetime.now() - timedelta(days=4)
                    waktu_limahari_lalu = datetime.now() - timedelta(days=5)
                    waktu_enamhari_lalu = datetime.now() - timedelta(days=6)
                    waktu_seminggu_lalu = datetime.now() - timedelta(weeks=1)
                    waktu_duaminggu_lalu = datetime.now() - timedelta(weeks=2)
                    waktu_tigaminggu_lalu = datetime.now() - timedelta(weeks=3)
                    waktu_empatminggu_lalu = datetime.now() - timedelta(weeks=4)
                    waktu_sebulan_lalu = datetime.now() - timedelta(weeks=5)
                    waktu_duabulan_lalu = datetime.now() - timedelta(weeks=8)
                    waktu_tigabulan_lalu = datetime.now() - timedelta(weeks=12)
                    waktu_empatbulan_lalu = datetime.now() - timedelta(weeks=16)

                    # mengubah string "seminggu lalu" menjadi objek datetime
                    if 'jam lalu' in review_time.lower() or 'menit lalu' in review_time.lower() or 'baru saja' in review_time.lower():
                        review_time = waktu_hari_ini
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "1 hari lalu":
                        review_time = waktu_sehari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")
                    
                    if review_time == "2 hari lalu":
                        review_time = waktu_duahari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")
                    
                    if review_time == "3 hari lalu":
                        review_time = waktu_tigahari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "4 hari lalu":
                        review_time = waktu_empathari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "5 hari lalu":
                        review_time = waktu_limahari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "6 hari lalu":
                        review_time = waktu_enamhari_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "seminggu lalu":
                        review_time = waktu_seminggu_lalu
                        review_time = review_time.strftime("%Y-%m-%d")
                    
                    if review_time == "2 minggu lalu":
                        review_time = waktu_duaminggu_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "3 minggu lalu":
                        review_time = waktu_tigaminggu_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "4 minggu lalu":
                        review_time = waktu_empatminggu_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "sebulan lalu":
                        review_time = waktu_sebulan_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "2 bulan lalu":
                        review_time = waktu_duabulan_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "3 bulan lalu":
                        review_time = waktu_tigabulan_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                    if review_time == "4 bulan lalu":
                        review_time = waktu_empatbulan_lalu
                        review_time = review_time.strftime("%Y-%m-%d")

                except:
                    review_time = None
            
                try:
                    review_text = review_detail.find_element(By.XPATH,"div/div/div[4]/div[2]/div/span[1]").text
                except:
                    review_text = None
            
                if reviewer_name is not None:
                    reviews.append({
                        "review-id": review_id,
                        "reviewer_name": reviewer_name,
                        "review_star": review_star,
                        "review_time": review_time,
                        "review_text": review_text
                    })
        except :
            reviews = None

  
        addressComponent = { 
            "district" : district,
            "city" : city,
            "province" : province,
            "postCode" : kode_pos
            }
        

        result_detail = {
            "tenantDesc": desc,
            "fullAddress": full_address,
            "plusCode" : plus_code,
            "addressComponent" : addressComponent,
            "locatedIn": located_in,
            "schedule": schedule_dict,
            "phone": phone,
            "website" : website,
            "popularHours" : popular_times, 
            "photoUrl" : photo_url,
            "reviews": reviews,
            "onlineDelivery" : gofood_list
        }

        item["details"] = result_detail
        insert_new_data(item)

        row_ = row_+1
    
    print("scraping finished, prepare to process output json")
    
    return list_all

if __name__ == "__main__":
    result = SeleniumExtractor("Restaurants","Padang, Sumatera Barat")
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
    filename = "output-{}.json".format(now_str)
    current_directory = os.getcwd()

    file_path = os.path.join(current_directory, filename)

    with open(file_path, "w") as output_file:
        json_str = json.dumps(result, indent=4)
        output_file.write(json_str)
    
    print("output json created")



