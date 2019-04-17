import time
import shutil
import xml.etree.ElementTree as ET
import wx.grid as gridlib
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
chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("start-maximized")
# =============================================================================


def upload(path):
    driver = webdriver.Chrome(executable_path=chromedriver_exe, chrome_options=chrome_options)
    driver.get("http://www.e-guvernare.ro/redirectfunic.htm")
    time.sleep(15)
    try:   #wait for page to load
        element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.NAME, "linkdoc"))
                )
    finally:
        irg = 1
    # create and launch unpack command to pdftk
    print(path)
    unpack(path)

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
    driver.find_element_by_name('linkdoc').send_keys(self.pathnames[i])
    driver.find_element_by_xpath('//input[@value="Trimite"]').click()
    time.sleep(5)

    #get document data (index + CUI)
    index = driver.find_element_by_xpath("//b[@style='color: #000000']").text
    master_table = db["master"]
    master_data = {"index": index,
                    "type": "null",
                    "CUI": CUI,
                    "year": year,
                    "month": month,
                    "verified": 0,
                    "state": "null"}


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
