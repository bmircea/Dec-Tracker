import os
import json
import sqlite3
import wx
from auto import *


with open("config.json", "r+") as f:
    config = json.load(f)
    f.close()


path = config["PATHS"]["main"]
dec_path = os.path.join(path, "dec")
pdf_path = os.path.join(path, "recipise")
chromedriver_exe = config["PATHS"]["chromedriver"]
xml_path = os.path.join(path, "DecUnica.xml")
headless = config["PATHS"]["headless"]
firme = config["firme"]

# Connect and create cursor

conn = sqlite3.connect("store.db")
c = conn.cursor()

##Create tables
c.execute('''SELECT * FROM CLIENTS WHERE generated_id=20''')

print(c.fetchone())


class MainFrame(wx.Frame):
    """Derive a new class of Frame."""
    """Main window. When clicking a button, a new window will be called. See other classes below"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 500))
        self.CreateStatusBar() # bottom status bar
        filemenu = wx.Menu()
        filemenu.Append(wx.ID_ABOUT, "&About", "Info")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)

        #Create sizer and add buttons
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        submit = wx.Button(self, wx.ID_ANY, "Depune")
        verify = wx.Button(self, wx.ID_ANY, "Verifica")
        database = wx.Button(self, wx.ID_ANY, "Baza de date")
        self.sizer.Add(submit, 1, wx.EXPAND)
        self.sizer.Add(verify, 1, wx.EXPAND)
        self.sizer.Add(database, 1, wx.EXPAND)

        #Bind events
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, submit)
        self.Bind(wx.EVT_BUTTON, self.OnVerify, verify)
        self.Bind(wx.EVT_BUTTON, self.OnDatabase, database)

        self.sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer2.Add(self.sizer, 0, wx.EXPAND)

        self.SetSizer(self.sizer2)
        self.SetAutoLayout(1)
        self.sizer2.Fit(self)
        self.Show(True)

    def OnSubmit(self, e):
        test("sub")
        SubmitFrame = SubmitWindow(frame, "Submit")

    def OnVerify(self, e):
        test("verify")
        VerifyFrame = VerifyWindow(frame, "Verify")

    def OnDatabase(self, e):
        test("db")
        DatabaseFrame = DatabaseWindow(frame, "Database")

class SubmitWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500,200))
        load = wx.Button(self, wx.ID_ANY, "Load files", size=(100, 100), pos=(5, 5))
        submit = wx.Button(self, wx.ID_ANY, "Submit Files", size = (100, 100), pos=(120, 5))
        self.Bind(wx.EVT_BUTTON, self.openDialog, load)
        self.Bind(wx.EVT_BUTTON, self.up, submit)
        self.Show(True)



    def openDialog(self, e):
        with wx.FileDialog(self, "Open PDF File", style = wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.paths = fileDialog.GetPaths()
            text = "Fisiere : \n"
            for i in range(len(self.paths)):
                text += self.paths[i]
                text += "\n"
            print(text)


    def up(self, e):
        for i in range(len(self.paths)):
            upload(self.paths[i])

class VerifyWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500,200))
        self.CreateStatusBar() # bottom status bar
        filemenu = wx.Menu()
        filemenu.Append(wx.ID_ABOUT, "&About", "Info")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        self.Show(True)

class DatabaseWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(700,500))
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.choices = []
        for f in firme:
            self.choices.append(firme[f])

        self.choice = wx.Choice(self.panel, choices=self.choices, pos=(225, 50), size=(250, 50))

        self.list = wx.ListCtrl(self.panel, -1, pos =(0, 100), style = wx.LC_REPORT)
        self.list.InsertColumn(0, "Database Index", width=100)
        self.list.InsertColumn(1, "Index", width=100)
        self.list.InsertColumn(2, "Tip", width=100)
        self.list.InsertColumn(3, "Luna", width=100)
        self.list.InsertColumn(4, "An", width=100)
        self.list.InsertColumn(5, "Stare", width=200)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list, 0, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Show()

app = wx.App(False)
frame = MainFrame(None, "Tracker Declaratii")
app.MainLoop()
