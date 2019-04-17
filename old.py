# -*- coding: utf-8 -*-
import wx
import time
import shutil
import xml.etree.ElementTree as ET
import wx.grid as gridlib
import os
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from pymongo import MongoClient
from bson import ObjectId


with open("config.json", "r+") as f:
    config = json.load(f)
    f.close()
    
    
LOGGER.setLevel(logging.WARNING)
path = config["PATHS"]["main"]
dec_path = os.path.join(path, "dec")
pdf_path = os.path.join(path, "recipise")
chromedriver_exe = config["PATHS"]["chromedriver"]
xml_path = os.path.join(path, "DecUnica.xml")
headless = config["PATHS"]["headless"]



profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": pdf_path , "download.extensions_to_open": "applications/pdf"}

# =============================================================================
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("start-maximized")
# =============================================================================



client = MongoClient()
db = client['firme']
cnt = 0


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 300))

        # A button
        self.depuneButton =wx.Button(self, label="Depune", pos=(50, 50))
        self.verificaButton = wx.Button(self, label="Baze de date", pos=(150, 50))
        self.masterButton = wx.Button(self, label="Verifica toate declaratiile", pos=(300, 50))
        self.Bind(wx.EVT_BUTTON, self.OpenDepuneWindow, self.depuneButton)
        self.Bind(wx.EVT_BUTTON, self.OpenVerificaWindow, self.verificaButton)
        self.Bind(wx.EVT_BUTTON, self.VerificaNemonitorizat, self.masterButton)

        self.Show(True)

    def OpenDepuneWindow(self, event):
        depuneFrame = DepuneWindow(mainFrame, "Depune Declaratii")

    def OpenVerificaWindow(self, event):
        self.verificaFrame = VerificaWindow(mainFrame, "Verifica Declaratii")
    
    def VerificaNemonitorizat(self, event):
        table = db['master']
        driver = webdriver.Chrome(executable_path=chromedriver_exe)
        driver.get("http://www.anaf.ro/StareD112/")
        time.sleep(3)
        for post in table.find():
            #if not verified
            if post["verif"] == 0:
                #submit data
                driver.find_element_by_name("id").send_keys(post["index"])
                driver.find_element_by_name("cui").send_keys(post["cui"])
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
                        table.update_one({'index': post['index']}, {'$set': {'tip':tip, "state": state, "verif":1}})
                    else:
                        table.update_one({'index': post['index']}, {'$set': {"state": record.text, "verif":1}})
                #go and verify the next entry
                driver.get("http://www.anaf.ro/StareD112/")
                time.sleep(3)
                
        driver.quit()
        infoWindow = DepuneWindow.Info(self, "Am verificat toate declaratiile!", "Job terminat")
        
        
class DepuneWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 300))
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.files = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL,  pos=(200, 50), size=(200, 200))
        self.selectButton = wx.Button(self.panel, label="Selecteaza declaratii", size=(150, 35), pos=(50, 50))
        self.Bind(wx.EVT_BUTTON, self.openFileDialog, self.selectButton)
        self.uploadButton = wx.Button(self.panel, label="Incarca declaratii", size=(150, 35), pos=(50, 150))
        self.Bind(wx.EVT_BUTTON, self.uploadJob, self.uploadButton)

        self.Show(True)

    def openFileDialog(self, event):
        self.files.SetValue("")
        with wx.FileDialog(self, "Incarca fisiere: ",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.pathnames = fileDialog.GetPaths()
            text = "Fisiere : \n"
            for i in range(len(self.pathnames)):
                text += self.pathnames[i]
                text += " \n"
            self.files.SetValue(text)
    
    def Info(parent, message, caption):
        dig = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
        dig.ShowModal()
        dig.Destroy()
    
    
    def uploadJob(self, event):
        driver = webdriver.Chrome(executable_path=chromedriver_exe, chrome_options=chrome_options)
        driver.get("http://www.e-guvernare.ro/redirectfunic.htm")
        time.sleep(15)
        try:
            element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.NAME, "linkdoc"))
                    )
        finally:
            irg = 1
        for i in range(len(self.pathnames)):
           # create and launch unpack command to pdftk
           print(self.pathnames[i]) 
           cmd = "pdftk %s unpack_files output %s" % \
                (self.pathnames[i],
                 path)
           os.system(cmd)
            
            #extract data off xml
           e = ET.parse(xml_path)
           root = e.getroot()
           cui = root[0].attrib['cif']
           luna = root.attrib['luna_r']
           an = root.attrib['an_r']
           den = root[0].attrib['den']
           os.remove(xml_path)
           
           driver.find_element_by_name('linkdoc').send_keys(self.pathnames[i])
           driver.find_element_by_xpath('//input[@value="Trimite"]').click()
           time.sleep(5)
            
           #get decl data (index + cui)
           index = driver.find_element_by_xpath("//b[@style='color: #000000']").text
           master_table = db["master"]
           master_data = {"index": index,
                           "tip": "null",
                           "cui": cui,
                           "an": an,
                           "luna": luna, 
                           "verif": 0,
                           "state": "null"}
            
           master_id = master_table.insert_one(master_data).inserted_id
            
            
           table = db[cui]
           post = {"index":index,
                    "master_table_id":master_id}
           table.insert_one(post)
            
           if not(cui in config['firme']):
               js = open("config.json", "w+")
               config['firme'][cui] = den
               js.write(json.dumps(config))
               js.close()
            
            
        #move file to new dir
           shutil.move(self.pathnames[i], dec_path)
           new_paths = self.pathnames[i].split("\\")
           new_p = os.path.join(dec_path, new_paths[len(new_paths)-1])
           new_name = index + ".pdf"
           mod_p = os.path.join(dec_path, new_name)
           os.rename(new_p, mod_p)
          
        infoWindow = DepuneWindow.Info(self, "Am depus declarati!", "Job terminat")

class VerificaWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,300))
        self.panel = wx.Panel(self, wx.ID_ANY)
        #get options from db
        self.choices = db.collection_names(include_system_collections=False)
        for i in range(len(self.choices)):
            if not(self.choices[i] == 'master'):
                self.choices[i] = config['firme'][self.choices[i]]
            
        self.choice = wx.Choice(self.panel, choices=self.choices, pos=(50, 50), size=(150, 50))
        
        self.verificaButton = wx.Button(self.panel, label="Rapoarte baza de date", pos=(280, 50))
        
        self.Bind(wx.EVT_BUTTON, self.verificaOnline, self.verificaButton)
        
        self.Show(True)

    def verificaOnline(self, event):
        self.selc = self.choice.GetString(self.choice.GetSelection())
        cnt = db[self.selc].count()
        title = 'Baza de date declaratii: ' + self.selc
        databaseFrame = DatabaseWindow(mainFrame, title)
        

class DatabaseWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title,  size=(800,500))
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.index = 0
        
        self.list = wx.ListCtrl(self.panel, -1, style = wx.LC_REPORT)
        self.list.InsertColumn(0, "Database Index", width=100)
        self.list.InsertColumn(1, "Index", width=100)
        self.list.InsertColumn(2, "Tip", width=100)
        self.list.InsertColumn(3, "Luna", width=100)
        self.list.InsertColumn(4, "An", width=100)
        self.list.InsertColumn(5, "Stare", width=200)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 0, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)
        
        master_table = db["master"]
        table = db[list(config['firme'].keys())[list(config['firme'].values()).index(mainFrame.verificaFrame.selc)]]
        for post in table.find():
            mast_post = master_table.find_one({'_id': post['master_table_id']})
            self.list.InsertItem(self.index, str(post['master_table_id']))
            self.list.SetItem(self.index, 1, mast_post['index'])
            self.list.SetItem(self.index, 2, mast_post['tip'])
            self.list.SetItem(self.index, 3, mast_post['luna'])
            self.list.SetItem(self.index, 4, mast_post['an'])
            self.list.SetItem(self.index, 5, mast_post['state'])
            self.index += 1
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onClick, self.list)
        
        self.Show()
        
    def onClick(self, event):
        master_table = db["master"]
        oid = ObjectId(event.GetText())
        mast_post = master_table.find_one({'_id': oid})
        filename = mast_post['index'] + ".pdf"
        os.startfile(os.path.join(pdf_path, filename))
        

app = wx.App(False)
mainFrame = MainWindow(None, "Declaratii")
app.MainLoop()



