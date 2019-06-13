import time
import shutil
import xml.etree.ElementTree as ET
#import wx.grid as gridlib
import os
import json
import logging
import miner
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER


# =============================================================================
chrome_options = Options()
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("start-maximized")
# =============================================================================


def goto(add):
    #open web WebDriver
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(add)

def upload(path):
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://decl.anaf.mfinante.gov.ro/my.policy")
    # click button to verify certificate
    try:
        element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//input[@value="Prezentare certificat"]'))
        )
    finally:
        pass  #TODO: raise error when button not found
    driver.find_element_by_xpath('//input[@value="Prezentare certificat"]').click()

    #Deactivating PyAUtoGui for the moment, it can't handle background windows
    #time.sleep(1)
    #pyautogui.press('enter')
    #time.sleep(30)

    try:   #wait for page to load
        element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.NAME, "linkdoc"))
                )
    finally:
        pass
    #copy pdf file
    copyfile(path, "/PDF/temp.pdf")

    # create and launch unpack command to pdftk
    print(path)
    unpack(path, "/XML/DecUnica.xml")

    #extract data off xml
    e = ET.parse(xml_path)
    root = e.getroot()
    CUI = root[0].attrib['cif']
    month = root.attrib['luna_r']
    year = root.attrib['an_r']
    name = root[0].attrib['den']

    #delete XML afer parsing
    os.remove(xml_path)

    #submit document
    driver.find_element_by_name('linkdoc').send_keys(path)
    driver.find_element_by_xpath('//input[@value="Trimite"]').click()
    time.sleep(5)

    #get document data (index + CUI)
    index = driver.find_element_by_xpath("//b[@style='color: #000000']").text
    entry = {"index": index,
             "type": "null",   '''not known yet, will get it when verifying'''
             "CUI": CUI,
             "year": year,
             "month": month,
             "verified": 0}


    #if CUI is not already in the config file, add it
    if not(cui in config['firme']):
        js = open("config.json", "w+")
        config['firme'][cui] = den
        js.write(json.dumps(config))
        js.close()


    #move file to new dir
    shutil.move(path, dec_path)
    new_paths = path.split("\\")
    new_p = os.path.join(dec_path, new_paths[len(new_paths)-1])
    new_name = index + ".pdf"
    mod_p = os.path.join(dec_path, new_name)
    os.rename(new_p, mod_p)

def verify(index, CUI):
    goto("https://www.anaf.ro/StareD112/")
    #submit data
    driver.find_element_by_name("id").send_keys(index)
    driver.find_element_by_name("cui").send_keys(CUI)
    driver.find_element_by_xpath("//input[@type='submit']").click()
    time.sleep(2)

    #get the response data
    records = driver.find_elements_by_xpath("//tr[@align='left']")
    for record in records:
        print(record.text)
        if post["index"] in record.text:
            data = record.text.split(" ")
            tip = data[1]
            state = data[4]
            driver.get("https://www.anaf.ro/StareD112/ObtineRecipisa?numefisier="+ post["index"] +".pdf")
            '''TODO: Update DB'''
        else:
            '''TODO : Update DB'''
    time.sleep(1)
    #go and verify the next index

def test(x):
    print(x)
