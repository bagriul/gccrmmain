import pymongo
import requests
import json
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver
import json
import time
from lxml import html
import httplib2
import os
from datetime import datetime
from datetime import timedelta
import threading
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import traceback
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver
from bs4 import BeautifulSoup as bs
import telebot

client = pymongo.MongoClient('mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test?authSource=admin&replicaSet=atlas-8jvx35-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true')
db = client['galcontract_crm']
clients_collection = db['clients']
protocols_collection = db['protocols']
protocols_all_collection = db['protocols_all']
biprozorro_collection = db['biprozorro']
mailing_search_collection = db['mailing_search']
mailing_search_auctions_collection = db['mailing_search_auctions']
tg_users_collection = db['tg_users']
streams_collection = db['streams']
procuringEntity_auctions_collection = db['procuringEntity_auctions']
bot = telebot.TeleBot('')


def get_new_users():
    opts = selenium.webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.binary_location = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
    driver = selenium.webdriver.Chrome(options=opts)
    driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
    username_field = driver.find_element("id", "eLogin")
    password_field = driver.find_element("id", "ePassword")
    login_button = driver.find_element("id", "btnLogin")
    username_field.send_keys("7timoor@gmail.com")
    password_field.send_keys("l689^544333")
    login_button.click()
    time.sleep(1)
    driver.get(
        f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetMembers&page=1&rows=1000&sidx=id&sord=desc&TimeMark=55106503')
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
    users_text = driver.find_element("xpath", '/html/body/pre')
    users_info = json.loads(users_text.text)['rows']
    count = 0
    for user_info_short in users_info:
        user_id = user_info_short['id']
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/DataHandler.ashx?CN=0&CommandName=jGetDetailMember&id={user_id}')
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        user_text = driver.find_element("xpath", '/html/body/pre')
        user_info_long = json.loads(user_text.text)['member']
        # Exclude "documents" field from the second JSON
        user_info_long.pop("documents", None)
        user_info_long.pop("telephone", None)

        register_date_str = user_info_long['register_date']
        create_date_str = user_info_short['create_date']
        try:
            date_object = datetime.strptime(register_date_str, "%Y-%m-%dT%H:%M:%S.%f")
            formatted_date = date_object.strftime("%d-%m-%Y")
            formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
            user_info_long['register_date'] = formatted_date_object
        except ValueError:
            pass
        try:
            date_object = datetime.strptime(create_date_str, "%d.%m.%Y %H:%M:%S.%f")
            formatted_date = date_object.strftime("%d-%m-%Y")
            formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
            user_info_long['create_date'] = formatted_date_object
        except ValueError:
            pass

        #Add comment field
        user_info_long['comment'] = ''
        # Merge the two JSON objects
        document = {**user_info_short, **user_info_long}
        is_present = clients_collection.find_one({'id': user_id})
        if is_present is None:
            clients_collection.insert_one(document)
        elif is_present != document:
            clients_collection.find_one_and_replace(is_present, document)
        count += 1
        print(count)


def protocols():
    startDate = datetime.now().date() - relativedelta(days=60)

    def BidsInfo(startDate):
        opts = selenium.webdriver.ChromeOptions()
        opts.add_argument('--headless')
        opts.binary_location = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
        while True:
            try:
                driver = selenium.webdriver.Chrome(options=opts)
                break
            except:
                pass
        driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
        username_field = driver.find_element("id", "eLogin")
        password_field = driver.find_element("id", "ePassword")
        login_button = driver.find_element("id", "btnLogin")
        username_field.send_keys("7timoor@gmail.com")
        password_field.send_keys("l689^544333")
        login_button.click()
        time.sleep(1)
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetBids&page=1&rows=10000&sidx=b.dateModified&sord=desc&fvBidState_0=active&fvauctiondate_0=%20%3E%3D%20%27{startDate}%27&TimeMark=37624327')
        #driver.get('https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetBids&page=1&rows=10&sidx=b.dateModified&sord=desc&fvNumber_0=LRE001-UA-20231124-99230&TimeMark=44052601')
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        bidsText = driver.find_element("xpath", '/html/body/pre')
        bidsInfo = json.loads(bidsText.text)
        return bidsInfo

    def get_info_from_gc(tenderID):
        opts = selenium.webdriver.ChromeOptions()
        opts.add_argument('--headless')
        opts.binary_location = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
        while True:
            try:
                driver = selenium.webdriver.Chrome(options=opts)
                break
            except:
                pass
        driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
        username_field = driver.find_element("id", "eLogin")
        password_field = driver.find_element("id", "ePassword")
        login_button = driver.find_element("id", "btnLogin")
        username_field.send_keys("7timoor@gmail.com")
        password_field.send_keys("l689^544333")
        login_button.click()
        time.sleep(1)
        driver.get(f'https://sales.tsbgalcontract.org.ua/auction/{tenderID}')
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sellingEntity"]/div[1]/div/span')))
        except TimeoutException:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sellingEntity"]/div[1]/div/span')))
            except TimeoutException:
                pass
        try:
            first_code = driver.find_element("xpath",
                                             "(//span[@class='LotInfo' and (string-length(.) = 8 or string-length(.) = 10) and not(contains(., '.'))])[1]").text
            if ('SPE' in tenderID) or ('SPD' in tenderID):
                first_protocol = driver.find_element("xpath",
                                                     '(//div[span[contains(text(), "Період підписання протоколу")]]//span[@class="LotInfo"][2])[1]').text
                first_contract = driver.find_element("xpath",
                                                     '(//div[span[contains(text(), "Період оплати")]]//span[@class="LotInfo"][2])[1]').text
                not_a_winner_first = driver.find_element("xpath", '//*[@id="awards"]/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]').text
            elif 'LAE' in tenderID or 'LAP' in tenderID:
                first_protocol = driver.find_element("xpath", '(//div[span[contains(text(), "Період підписання протоколу")]])[1]').text[50:]
                first_contract = driver.find_element("xpath", '(//div[span[contains(text(), "Період підписання договору")]])[1]').text[49:]
                page = requests.get(f'https://marketplace.prozorro.sale/auction/{tenderID}')
                soup = bs(page.content, 'html.parser')
                td_tag = soup.find_all('td', attrs={'data-label': 'Рішення'})
                # Extract text from the <b> tag within the <td> tag
                try:
                    b_tag = td_tag[0].find('b')
                    if b_tag:
                        not_a_winner_first = b_tag.get_text()
                except:
                    not_a_winner_first = 'False'
            else:
                first_protocol = driver.find_element("xpath",
                                                     '(//div[span[contains(text(), "Період підписання протоколу")]]//span[@class="LotInfo"][2])[1]').text
                first_contract = driver.find_element("xpath",
                                                     '(//div[span[contains(text(), "Період підписання договору")]]//span[@class="LotInfo"][2])[1]').text
                not_a_winner_first = driver.find_element("xpath",
                                                         '//*[@id="awards"]/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]').text
        except Exception as e:
            print(e)
            first_code = None
            first_protocol = None
            first_contract = None
        try:
            second_code = driver.find_element("xpath",
                                             "(//span[@class='LotInfo' and (string-length(.) = 8 or string-length(.) = 10) and not(contains(., '.'))])[2]").text
            if ('SPE' in tenderID) or ('SPD' in tenderID):
                second_protocol = driver.find_element("xpath",
                                                      '(//div[span[contains(text(), "Період підписання протоколу")]]//span[@class="LotInfo"][2])[2]').text
                second_contract = driver.find_element("xpath",
                                                      '(//div[span[contains(text(), "Період оплати")]]//span[@class="LotInfo"][2])[2]').text
                not_a_winner_second = driver.find_element("xpath", '//*[@id="awards"]/div/div/div[3]/div/div/div/div[2]/div[3]/div[1]').text
            elif 'LAE' in tenderID or 'LAP' in tenderID:
                second_protocol = driver.find_element("xpath", '(//div[span[contains(text(), "Період підписання протоколу")]])[1]').text[50:]
                second_contract = driver.find_element("xpath", '(//div[span[contains(text(), "Період підписання договору")]])[1]').text[49:]
                page = requests.get(f'https://marketplace.prozorro.sale/auction/{tenderID}')
                soup = bs(page.content, 'html.parser')
                td_tag = soup.find_all('td', attrs={'data-label': 'Рішення'})
                # Extract text from the <b> tag within the <td> tag
                print(tenderID)
                try:
                    b_tag = td_tag[1].find('b')
                    if b_tag:
                        not_a_winner_second = b_tag.get_text()
                except:
                    not_a_winner_second = 'False'
            else:
                second_protocol = driver.find_element("xpath",
                                                      '(//div[span[contains(text(), "Період підписання протоколу")]]//span[@class="LotInfo"][2])[2]').text
                second_contract = driver.find_element("xpath",
                                                      '(//div[span[contains(text(), "Період підписання договору")]]//span[@class="LotInfo"][2])[2]').text
                not_a_winner_second = driver.find_element("xpath",
                                                          '//*[@id="awards"]/div/div/div[3]/div/div/div/div[2]/div[3]/div[1]').text
        except:
            second_code = None
            second_protocol = None
            second_contract = None
        try:
            if not_a_winner_first is None:
                not_a_winner_first = 'False'
        except UnboundLocalError:
            not_a_winner_first = 'False'
        try:
            if not_a_winner_second is None:
                not_a_winner_second = 'False'
        except UnboundLocalError:
            not_a_winner_second = 'False'
        print(not_a_winner_first, not_a_winner_second)
        return first_code, first_protocol, first_contract, second_code, second_protocol, second_contract, not_a_winner_first, not_a_winner_second


    def get_info_from_prozorro(tenderID):
        page = requests.get(f'https://marketplace.prozorro.sale/auction/{tenderID}')
        soup = bs(page.content, 'html.parser')
        stream = soup.find('div', class_='information-head__name').text
        is_present = streams_collection.find_one({'name': stream})
        if is_present is None:
            streams_collection.insert_one({'name': stream})
        price_string = soup.find('span', class_='news-card__price-sum news-card__price-sum--large').text
        price_cleaned = ''.join(c for c in price_string if c.isdigit() or c == ',')
        price_cleaned = price_cleaned.replace(',', '.')
        price = float(price_cleaned)
        # Find the <td> tag with the specified class
        """td_tag = soup.find_all('td', attrs={'data-label': 'Рішення'})
        # Extract text from the <b> tag within the <td> tag
        print(tenderID)
        try:
            b_tag = td_tag[0].find('b')
            if b_tag:
                not_a_winner_first = b_tag.get_text()
        except:
            not_a_winner_first = 'False'
        try:
            b_tag = td_tag[1].find('b')
            if b_tag:
                not_a_winner_second = b_tag.get_text()
        except:
            not_a_winner_second = 'False'"""
        return stream, price

    data_json = BidsInfo(startDate)
    bids = data_json['rows']
    count = 0
    for bid in bids:
        print(bid['tenderID'])
        do_update = protocols_collection.find_one({'id': bid['id'], 'statusTender': bid['statusTender']})
        if (do_update is not None) or ('TIE' in bid['tenderID']):
            print('Already exists and same status or TIE')
            continue
        try:
            confirm_date = bid["confirm_date"]
            dateModified = bid["dateModified"]
            id_tender = bid["id_tender"]
            page = requests.get(f'https://procedure.prozorro.sale/api/procedures/{id_tender}')
            data_json = page.json()
            description = data_json['description']['uk_UA']
            title = bid["title"]
            value_amount = bid["value_amount"]
            procuringEntity_id = bid["procuringEntity_id"]
            procuringEntity_name = bid["procuringEntity_name"]
            tenderID = bid["tenderID"]
            auction_date = bid["auction_date"]
            try:
                date_object = datetime.strptime(auction_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = date_object.strftime("%d-%m-%Y")
                formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
                auction_date = formatted_date_object
            except ValueError as e:
                print(e)
                pass
            tenderPeriod_endDate = bid["tenderPeriod_endDate"]
            dgfID = bid["dgfID"]
            guarantee_amount = bid["guarantee_amount"]
            status = bid["status"]
            StateText = bid["StateText"]
            id_member = bid["id_member"]
            code = bid["code"]
            short_name = bid["short_name"]
            promo_code = bid["promo_code"]
            Short_mannager_name = bid["Short_mannager_name"]
            statusTender = bid["statusTender"]
            who_fixed = bid["who_fixed"]
            date_fixed = bid["date_fixed"]
            link_prozorro = f'https://prozorro.sale/auction/{tenderID}'
            link_gc = f'https://sales.tsbgalcontract.org.ua/auction/{tenderID}'
            request = requests.get(f'https://marketplace.prozorro.sale/auction/{tenderID}')
            soup = bs(request.content, 'html.parser')
            newstatus = soup.find('div', class_='news-card__status').text.strip()
            newprotokol_div = soup.find('div', class_='table-info__date-opening')
            first_code, first_protocol, first_contract, second_code, second_protocol, second_contract, not_a_winner_first, not_a_winner_second = get_info_from_gc(
                tenderID)
            stream, price = get_info_from_prozorro(tenderID)
            if first_code == code:
                protocol_enddate = first_protocol
                contract_enddate = first_contract
            elif second_code == code:
                protocol_enddate = second_protocol
                contract_enddate = second_contract
            else:
                protocol_enddate = None
                contract_enddate = None
            try:
                if protocol_enddate is not None:
                    try:
                        date_object = datetime.strptime(protocol_enddate, "%d.%m.%Y %H:%M")
                    except:
                        date_object = datetime.strptime(protocol_enddate, "%d.%m.%Y %H:%M:%S")
                    formatted_date = date_object.strftime("%d-%m-%Y")
                    formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
                    protocol_enddate = formatted_date_object
            except ValueError or TypeError:
                pass
            try:
                if contract_enddate is not None:
                    try:
                        date_object = datetime.strptime(contract_enddate, "%d.%m.%Y %H:%M")
                    except:
                        date_object = datetime.strptime(contract_enddate, "%d.%m.%Y %H:%M:%S")
                    formatted_date = date_object.strftime("%d-%m-%Y")
                    formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
                    contract_enddate = formatted_date_object
            except ValueError or TypeError:
                pass
            try:
                try:
                    newprotokol = newprotokol_div.find_all('span')[1].text[:-6]
                    date_object = datetime.strptime(newprotokol, "%d.%m.%Y")
                except ValueError:
                    newprotokol = soup.find_all('td', class_='table-info__td width-30').text[:-6]
                    date_object = datetime.strptime(newprotokol, "%d.%m.%Y")
                formatted_date = date_object.strftime("%d-%m-%Y")
                formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
                newprotokol = formatted_date_object
            except AttributeError or ValueError or TypeError:
                newprotokol = None

            def add_business_days(start_date, days_to_add):
                current_date = start_date

                for _ in range(days_to_add):
                    current_date += timedelta(days=1)
                    while current_date.weekday() in {5, 6}:  # Skip Saturday (5) and Sunday (6)
                        current_date += timedelta(days=1)

                return current_date

            if newprotokol is not None:
                sign_enddate = add_business_days(newprotokol, 3)
            elif newprotokol is None:
                sign_enddate = None
            document = {
                'auction_date': auction_date,
                'id': bid['id'],
                'confirm_date': confirm_date,
                'dateModified': dateModified,
                'id_tender': id_tender,
                'title': title,
                'value_amount': value_amount,
                'procuringEntity_id': procuringEntity_id,
                'procuringEntity_name': procuringEntity_name,
                'tenderID': tenderID,
                'tenderPeriod_endDate': tenderPeriod_endDate,
                'dgfID': dgfID,
                'guarantee_amount': guarantee_amount,
                'status': status,
                'StateText': StateText,
                'id_member': id_member,
                'code': code,
                'short_name': short_name,
                'promo_code': promo_code,
                'Short_mannager_name': Short_mannager_name,
                'statusTender': statusTender,
                'who_fixed': who_fixed,
                'date_fixed': date_fixed,
                'newstatus': newstatus,
                'newprotokol': newprotokol,
                'link_prozorro': link_prozorro,
                'link_gc': link_gc,
                'protocol_enddate': protocol_enddate,
                'contract_enddate': contract_enddate,
                'comment': '',
                'stream': stream,
                'price': price,
                'description': description,
                'sign_enddate': sign_enddate
            }
            is_present = protocols_collection.find_one({'id': bid['id']})
            not_to_add_statuses = ['Аукціон відмінено', 'Аукціон не відбувся']
            not_check_lower_second_place = ['Прийняття заяв на участь', 'Аукціон']
            not_a_winner_statuses = ['Учасник не став переможцем', 'Дискваліфіковано']
            print(tenderID)
            print(not_a_winner_first, not_a_winner_second)
            if (newstatus in not_to_add_statuses) or (
                    (newstatus not in not_check_lower_second_place) and (protocol_enddate is None)) or (
                    (any(status in not_a_winner_first for status in not_a_winner_statuses)) and (first_code == code)) or (
                    (any(status in not_a_winner_second for status in not_a_winner_statuses)) and (second_code == code)):
                try:
                    protocols_collection.delete_one({'id': bid['id']})
                except:
                    pass
                print('Do not add')
            elif (code == second_code) and (any(status not in not_a_winner_first for status in not_a_winner_statuses)):
                print('Second place. First place didn"t lose')
            elif (code != first_code) and (code != second_code):
                print('Not first or second place')
            elif is_present is None:
                protocols_collection.insert_one(document)
                print('Added')
            elif is_present != document:
                protocols_collection.find_one_and_replace(is_present, document)
                print('Updated')
            else:
                print('Other reason')
        except:
            print(traceback.format_exc())
        count += 1
        print(count)
            
            
def get_bi_prozorro():
    opts = selenium.webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = selenium.webdriver.Chrome(options=opts)
    driver.get('https://bi.prozorro.sale/#/participants')
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.XPATH,
                                               '//*[@id="7eea4556-fdab-4c66-8e6e-415181068828_content"]/div/div[2]/div[1]/div/table/tbody/tr/td[2]/div/div/span')))
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="7eea4556-fdab-4c66-8e6e-415181068828-header-6"]/div/div/div/span')))

    sort_button = driver.find_element('xpath', '//*[@id="7eea4556-fdab-4c66-8e6e-415181068828-header-6"]/div/div/div/span')
    sort_button.click()
    time.sleep(3)
    sort_button.click()
    time.sleep(3)
    all_codes = driver.find_elements("xpath",
                                     '//*[@id="7eea4556-fdab-4c66-8e6e-415181068828_content"]/div/div[2]/div[1]/div/table/tbody/tr/td[2]/div/div/span')
    all_codes_text = []
    for element in all_codes:
        if len(element.text) > 1:
            all_codes_text.append(element.text)

    for code in all_codes_text:
        print(code)
        page = driver.get(
            f"https://bi.prozorro.sale/?select=%D0%9A%D0%BE%D0%B4%20%D1%83%D1%87%D0%B0%D1%81%D0%BD%D0%B8%D0%BA%D0%B0/[%22{code}%22]#/participantsCard")

        # Specify the XPath of the element you want to wait for (code)
        element_xpath = '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[2]/td[2]/div/div/span'

        # Define a custom expected condition to wait until the length of the text inside the element is more than 1
        class text_length_greater_than(object):
            def __init__(self, locator, length):
                self.locator = locator
                self.length = length

            def __call__(self, driver):
                element = driver.find_element(*self.locator)  # Finding the referenced element
                if len(element.text) > self.length:
                    return element
                else:
                    return False

        # Wait until the length of the text inside the element is more than 1
        element = wait.until(text_length_greater_than((By.XPATH, element_xpath), 1))

        while True:
            try:
                name = driver.find_element("xpath",
                                           '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[1]/td[2]/div/div/span')
                code = driver.find_element("xpath",
                                           '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[2]/td[2]/div/div/span')
                representative = driver.find_element("xpath",
                                                     '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[3]/td[2]/div/div/span')
                phone = driver.find_element("xpath",
                                            '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[4]/td[2]/div/div/span')
                email = driver.find_element("xpath",
                                            '//*[@id="3d5f6835-9915-420f-9255-5204b0d5562f_content"]/div/div[2]/div[1]/div/table/tbody/tr[5]/td[2]/div/div/span')

                time.sleep(10)
                # Specify the XPath to find the elements
                auctions_xpath = '//*[@id="83771584-877f-4bba-91f1-6b2fcd581488_content"]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/span'
                # Find all elements matching the specified XPath
                auctions = driver.find_elements(By.XPATH, auctions_xpath)
                all_auctions_text = []
                for auction in auctions:
                    all_auctions_text.append(auction.text)
                while ("" in all_auctions_text):
                    all_auctions_text.remove("")
                all_auctions = []
                for i in all_auctions_text:
                    if i not in all_auctions:
                        all_auctions.append(i)

                print(name.text, code.text, representative.text, phone.text, email.text, all_auctions)
                document = {'name': name.text,
                            'code': code.text,
                            'representative': representative.text,
                            'phone': phone.text,
                            'email': email.text,
                            'comment': '',
                            'auctions': all_auctions}
                is_present = biprozorro_collection.find_one({'code': code.text})
                if is_present is None:
                    biprozorro_collection.insert_one(document)
                elif is_present != document:
                    biprozorro_collection.find_one_and_replace(is_present, document)
                break
            except Exception as e:
                print(e)
                pass
    driver.quit()


def check_mailing_auctions():
    searches = mailing_search_collection.find()
    for search in searches:
        page = requests.get(search['link'])
        soup = bs(page.content, 'html.parser')
        cards = soup.find_all('a', class_='sc-main__title')
        for card in cards:
            href = card.get('href')
            is_present = mailing_search_auctions_collection.find_one({'href': href})
            if is_present is None:
                mailing_search_auctions_collection.insert_one({'href': href})
                tg_users = tg_users_collection.find()
                for tg_user in tg_users:
                    bot.send_message(tg_user['tg_id'], f'Новий аукціон за вашим пошуком:\n'
                                                       f'https://prozorro.sale{href}')


def get_procuringEntity_auctions():
    opts = selenium.webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.binary_location = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
    driver = selenium.webdriver.Chrome(options=opts)
    driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
    username_field = driver.find_element("id", "eLogin")
    password_field = driver.find_element("id", "ePassword")
    login_button = driver.find_element("id", "btnLogin")
    username_field.send_keys("7timoor@gmail.com")
    password_field.send_keys("l689^544333")
    login_button.click()
    time.sleep(1)
    driver.get(
        f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetMembers&page=1&rows=10000&sidx=id&sord=desc&fvmemberType_0=901&fvmemberType_1=905&fvmemberType_2=906&fvmemberType_3=907&fvmemberType_4=908&fvmemberType_5=909&fvmemberType_6=910&fvmemberType_7=911&fvmemberType_8=912&fvmemberType_9=913&fvmemberType_10=914&fvmemberType_11=915&fvmemberType_12=916&fvmemberType_13=917&TimeMark=58910841')
    wait = WebDriverWait(driver, 60)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
    users_text = driver.find_element("xpath", '/html/body/pre')
    users_info = json.loads(users_text.text)['rows']
    count = 0
    for user_info_short in users_info:
        user_id = user_info_short['id']
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/DataHandler.ashx?CN=0&CommandName=jGetDetailMember&id={user_id}')
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        user_text = driver.find_element("xpath", '/html/body/pre')
        user_info_long = json.loads(user_text.text)['member']
        # Exclude "documents" field from the second JSON
        user_info_long.pop("documents", None)
        user_info_long.pop("telephone", None)

        register_date_str = user_info_long['register_date']
        create_date_str = user_info_short['create_date']
        code = user_info_short['code']
        try:
            date_object = datetime.strptime(register_date_str, "%Y-%m-%dT%H:%M:%S.%f")
            formatted_date = date_object.strftime("%d-%m-%Y")
            formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
            user_info_long['register_date'] = formatted_date_object
        except ValueError:
            pass
        try:
            date_object = datetime.strptime(create_date_str, "%d.%m.%Y %H:%M:%S.%f")
            formatted_date = date_object.strftime("%d-%m-%Y")
            formatted_date_object = datetime.strptime(formatted_date, "%d-%m-%Y")
            user_info_long['create_date'] = formatted_date_object
        except ValueError:
            pass

        #Add comment field
        user_info_long['comment'] = ''
        # Merge the two JSON objects
        document = {**user_info_short, **user_info_long}
        is_present = clients_collection.find_one({'id': user_id})
        if is_present is None:
            clients_collection.insert_one(document)
        elif is_present != document:
            clients_collection.find_one_and_replace(is_present, document)
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetPositions&page=1&rows=1000&sidx=dateModified&sord=desc&filter_type=filter&fvMember_0={code}&action=Y&status=all&TimeMark=58766247')
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        bids_text = driver.find_element("xpath", '/html/body/pre')
        bids = json.loads(bids_text.text)['rows']
        for bid in bids:
            is_present = procuringEntity_auctions_collection.find_one({'id': bid['id']})
            if is_present is None:
                procuringEntity_auctions_collection.insert_one(bid)
            else:
                pass
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetPositions&page=1&rows=10&sidx=dateModified&sord=desc&filter_type=filter&fvMember_0={code}&action=N&status=all&TimeMark=43001539')
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        bids_text = driver.find_element("xpath", '/html/body/pre')
        bids = json.loads(bids_text.text)['rows']
        for bid in bids:
            is_present = procuringEntity_auctions_collection.find_one({'id': bid['id']})
            if is_present is None:
                procuringEntity_auctions_collection.insert_one(bid)
            else:
                pass
        count += 1
        print(count)


def get_all_protocols():
    startDate = datetime.now().date() - relativedelta(days=7300)

    def BidsInfo(startDate):
        opts = selenium.webdriver.ChromeOptions()
        opts.add_argument('--headless')
        opts.binary_location = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
        while True:
            try:
                driver = selenium.webdriver.Chrome(options=opts)
                break
            except:
                pass
        driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
        username_field = driver.find_element("id", "eLogin")
        password_field = driver.find_element("id", "ePassword")
        login_button = driver.find_element("id", "btnLogin")
        username_field.send_keys("7timoor@gmail.com")
        password_field.send_keys("l689^544333")
        login_button.click()
        time.sleep(1)
        driver.get(
            f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetBids&page=1&rows=10000&sidx=b.dateModified&sord=desc&fvBidState_0=active&fvauctiondate_0=%20%3E%3D%20%27{startDate}%27&TimeMark=37624327')
        # driver.get('https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetBids&page=1&rows=10&sidx=b.dateModified&sord=desc&fvNumber_0=LLE001-UA-20231212-75574&TimeMark=44052601')
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        bidsText = driver.find_element("xpath", '/html/body/pre')
        bidsInfo = json.loads(bidsText.text)
        return bidsInfo


    data_json = BidsInfo(startDate)
    bids = data_json['rows']
    count = 0
    for bid in bids:
        do_update = protocols_all_collection.find_one({'id': bid['id']})
        if do_update is not None:
            print(bid['tenderID'])
            print('Already exists')
            continue
        request = requests.get(f'https://marketplace.prozorro.sale/auction/{bid["tenderID"]}')
        soup = bs(request.content, 'html.parser')
        try:
            description = soup.find('div', class_='information-text').text
        except AttributeError:
            continue
        stream = soup.find('div', class_='information-head__name').text
        bid['stream'] = stream
        bid['description'] = description
        protocols_all_collection.insert_one(bid)

        count += 1
        print(count)


while True:
    get_new_users()
    protocols()
    # get_bi_prozorro()
    # check_mailing_auctions()
    get_procuringEntity_auctions()
