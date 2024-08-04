from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, NoSuchWindowException, ElementNotInteractableException, NoSuchElementException
import re
import datetime
from datetime import date
from bs4 import BeautifulSoup
import os
import base64
from PIL import Image
from io import BytesIO
import subprocess
import pytesseract
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure,ConfigurationError
from mongoengine import connect
from mongoengine import DoesNotExist
from html.parser import HTMLParser
from parser import parse_description_items, parse_full_text, parse_full_text_image, parse_abstract_attached_drawings, parse_drawings_of_specification,parse_legal_status, parse_homology, parse_citation, parse_cited
from mongo_patent import MongoPatent
from dataclass_patent import DataPatent

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
email = "do.infinitely@gmail.com"
password = "P@ssw0rd"
start_date = datetime.date(year=1790, month=7, day=31)
second_start_date = datetime.date(year=1862, month=1, day=1)
end_date = datetime.date(year=2024, month=7, day=15)

MONGO_URI = "mongodb+srv://doinfinitely:EhTL2eZBcnbmnEzF@cluster0.tvmr4ar.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PYMONGO_CLIENT = MongoClient(MONGO_URI, server_api=ServerApi('1'))
connect(host=MONGO_URI)
try:
    PYMONGO_CLIENT.admin.command("ping")
    print("successfully pinged mongo")
    print("logging into site, doing captcha...")
except ConnectionFailure:
    print("fail")


def init():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get('https://pss-system.cponline.cnipa.gov.cn/login')
    time.sleep(20)
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((
        By.TAG_NAME, 'body'
    )))
    app = driver.find_element(By.CSS_SELECTOR, 'button')
    app.click()
    driver.get('https://pss-system.cponline.cnipa.gov.cn/login')
    login(driver)
    return driver

def is_logged_in(driver):
    try:
        time.sleep(5)
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        ele = driver.find_element(By.CSS_SELECTOR, 'div[class=btn]')
        return True
    except:
        driver.find_element(By.CSS_SELECTOR, 'div.codeBox').click()
        return False

def clear_form(driver) :
    driver.find_elements(By.CSS_SELECTOR, 'input')[0].clear()
    driver.find_elements(By.CSS_SELECTOR, 'input')[1].clear()
    driver.find_elements(By.CSS_SELECTOR,'input')[2].clear()
    
def login(driver) :
    WebDriverWait(driver,50).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, 'div.lang-box > div:first-child').click()
    while not is_logged_in(driver):
        try:
            time.sleep(5)
            clear_form(driver)
            user_email = driver.find_elements(By.CSS_SELECTOR, 'input')[0]
            user_password = driver.find_elements(By.CSS_SELECTOR, 'input')[1]
            code_input = driver.find_elements(By.CSS_SELECTOR,'input')[2]
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'form button')
            captcha_code = driver.find_element(By.CSS_SELECTOR,'.codeBox img')
            base64 = captcha_code.get_attribute('src')
            reversed_code = convertCaptcha(base64)
            reversed_code = re.sub(r'\[^0-9]+', '', reversed_code)
            reversed_code = reversed_code[:min(4,len(reversed_code))]
            user_email.send_keys(email)
            time.sleep(0.5)
            user_password.send_keys(password)
            time.sleep(0.5)
            code_input.send_keys(reversed_code)
            submit_btn.click()
        except:
            time.sleep(1)
        
    return

def convertCaptcha(data) :
    base64_image = data
    base64_image = base64_image.split(',')[1]
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))
    image.save('captcha_image.png')
    text = pytesseract.image_to_string(image)

    return text
    
def wait_for_field(driver):
    placeholder = "Please enter keywords, application number / publication number, applicant / inventor, application date / publication date, IPC classification number / CPC classification number, and the system will intelligently identify and retrieve them according to the rules"
    while True:
        try:
            for element in driver.find_elements(By.XPATH, '//input'):
                if element.get_attribute('placeholder') == placeholder:
                    return driver, element
        except StaleElementReferenceException:
            pass

def get_li_items(driver, pub_no):
   
    driver.switch_to.window(driver.window_handles[2])
    index = 0
    try:
        os.mkdir('data/{0}'.format(pub_no))
    except FileExistsError:
        driver.switch_to.window(driver.window_handles[1])
        return 
    time.sleep(5)
    header = "description_items"
    print(header)
    with open('data/{0}/{1}_{2}.html'.format(pub_no, header, str(index).zfill(20)), 'w') as f:
        f.write(driver.page_source)
    try:
        elements = driver.find_elements(By.XPATH, '//li')
        for element in elements:
            if element.get_attribute("data-v-3596aade") is not None and "Quick Search" not in element.get_attribute('innerHTML') and "Search results" not in element.get_attribute('innerHTML') and "Detailed view" not in element.get_attribute('innerHTML'):
                if element.get_attribute("class") != "activeli":
                    header = element.get_attribute('innerHTML')
                    header = header.replace('<!---->', '')
                    header = header.strip().lower().replace(" ", "_")
                    print(header)
                    index = 0
                    while True:
                        try:
                            #element.click()
                            driver.execute_script ("arguments[0].click();",element)
                            time.sleep(5)
                            with open('data/{0}/{1}_{2}.html'.format(pub_no, header, str(index).zfill(20)), 'w') as f:
                                f.write(driver.page_source)
                            break
                        except  :
                            pass
                        except ElementClickInterceptedException:
                            pass
                        except NoSuchElementException:
                            pass
                    try:
                        elem = driver.find_elements(By.XPATH, '//button[@class="btn-next"]')[0]
                    except IndexError:
                        continue
                    while elem.get_attribute("disabled") is None:
                        while True:
                            try:
                                elem.click()
                                index += 1
                                time.sleep(10)
                                with open('data/{0}/{1}_{2}.html'.format(pub_no, header, str(index).zfill(20)), 'w') as f:
                                    f.write(driver.page_source)
                                break
                            except ElementClickInterceptedException:
                                pass
                                
        save_patent_to_mongo(pub_no)
            
    except StaleElementReferenceException:
        pass
    driver.switch_to.window(driver.window_handles[1])
        
def save_patent_to_mongo(pub_no):
    data_descrption_items = parse_description_items(pub_no)
#    data_full_text = parse_full_text(pub_no)
    data_full_text_image = parse_full_text_image(pub_no)
    data_abstract_attached_drawings = parse_abstract_attached_drawings(pub_no)
    data_drawings_of_specification = parse_drawings_of_specification(pub_no)
#    data_legal_stauts = parse_legal_status(pub_no)
#    data_homology = parse_homology(pub_no)
#    data_citation = parse_citation(pub_no)
#    data_cited = parse_cited(pub_no)
    
    patent_number = data_descrption_items["Application No."]
    pdf_url = data_full_text_image["Pdf url"]
    try:
        priority_date = data_descrption_items["Priority date"].split(';')
        if priority_date[-1] == '':
            priority_date.pop()
    except KeyError:
        priority_date = []
    try:
        filing_date = data_descrption_items["Application Date"]
    except KeyError:
        filing_date = date(1, 1, 1)
    publication_date = data_descrption_items["Publication Date"]
    try:
        abstract = data_descrption_items["Abstract"]
    except:
        abstract = ''
    specification = ''
    claims = []
    try:
        title = data_descrption_items["Invention Title"]
    except KeyError:
        title = ''
    jurisdiction = 'China'
    try:
        inventors = data_descrption_items["Inventor"].split(";")
    except KeyError:
        inventors = []
    assignees = []
    status = ''
    classifications = ''
    abstract_images = data_abstract_attached_drawings["Abstract attached drawings Urls"]
    specification_images = data_drawings_of_specification["Attached drawings of the specification urls"]
    
    existing_patent = MongoPatent.objects(patent_number=patent_number).first()
    if existing_patent:
        return
    else:
        MongoPatent(
            patent_number = patent_number,
            pdf_url = pdf_url,
            priority_date = priority_date,
            filing_date = filing_date,
            publication_date = publication_date,
            abstract = abstract,
            specification = specification,
            claims = claims,
            title = title,
            jurisdiction = jurisdiction,
            inventors = inventors,
            assignees = assignees,
            status = status,
            classifications = classifications,
            abstract_images = abstract_images,
            specification_images = specification_images
        ).save()
        
    return
   

def click_publications(driver):
    
    time.sleep(10)
    elements = driver.find_elements(By.XPATH, '//div[@class="el-tooltip"]/span')
    for element in elements:
        try:
            for prop in element.get_property('attributes'):
                try:
                    m = re.match(r'data-.+?-.+', element.get_property('attributes')[prop]['name'])
                    if m and element.get_property('attributes')[prop]['name'] not in ["data-v-13dd1d30", "data-v-359b7a02"]:
                        m = re.fullmatch(r'[A-Z0-9;]+', element.get_attribute('innerHTML'))
                        if m:
                            pub_no = element.get_attribute('innerHTML')
                            print(pub_no)
                            while True:
                                try:
                                    #element.click()
                                    driver.execute_script ("arguments[0].click();",element)
                                    time.sleep(1)
                                    get_li_items(driver, pub_no)
                                    break
                                except ElementClickInterceptedException:
                                    pass
                            break
                except KeyError:
                    pass
                except TypeError:
                    pass
                except NoSuchElementException:
                    save_patent_to_mongo(pub_no)
                    driver.switch_to.window(driver.window_handles[1])
        except NoSuchElementException:
            driver.switch_to.window(driver.window_handles[1])

def get_publications(driver):
    driver.switch_to.window(driver.window_handles[1])
    click_publications(driver)
    try:
        element = driver.find_elements(By.XPATH, '//button[@class="btn-next"]')[0]
    except IndexError:
        return
    while element.get_attribute("disabled") is None:
        while True:
            try:
                element.click()
                break
            except ElementClickInterceptedException:
                pass
        time.sleep(5)
        click_publications(driver)
        element = driver.find_elements(By.XPATH, '//button[@class="btn-next"]')[0]


driver = init()
print("logged in succesfully")
driver, element = wait_for_field(driver)
element.clear()
current_date = start_date
print(current_date)
element.send_keys(current_date.isoformat())
element = driver.find_elements(By.XPATH, '//div[@class="btn"]')[0]
driver.execute_script ("arguments[0].click();",element)
time.sleep(5)
get_publications(driver)
current_date = second_start_date

while current_date < end_date:
    print(current_date)
    driver.switch_to.window(driver.window_handles[0])
    driver, element = wait_for_field(driver)
    element.clear()
    element.send_keys(current_date.isoformat())
    element = driver.find_elements(By.XPATH, '//div[@class="btn"]')[0]
    element.click()
    time.sleep(5)
    get_publications(driver)
    current_date = current_date + datetime.timedelta(days=1)
