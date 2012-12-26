'''
Copyright (c) 2012, Jesper Derehag
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
  * Neither the name of the <organization> nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL JESPER DEREHAG BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
from Tkinter import *
import tkFileDialog
import Pmw
from TabStockBrowser import TabStockBrowser
from TabStockPredictor import TabStockPredictor

from Crawler import Parser
from Db.StockCsvReader import StockCsvReader


class StockRobotMainGui(Tk):
    def __init__(self, db, crawler):
        Tk.__init__(self)
        Pmw.initialise(self)
        self.crawler = crawler
        self.db = db
        
        self.crawler.registerObserver(self)
        
        self.title("StockRobot")
        self.protocol("WM_DELETE_WINDOW", self.__del__)
        self.geometry("1000x600")
        
        # Menubar
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        
        menu.add_command(label="insert stock csv..", command=self.insertStockCsv)
        
        menu.add_command(label="Execute crawl from seeds", command=self.executeCrawler, accelerator="Ctrl+E")
        self.bind('<Control-e>', self.executeCrawler)
        menu.add_command(label="Execute linkscraping on affarsvarlden", command=self.executeAffarsvarldenLinkScraper, accelerator="Ctrl+A")
        self.bind('<Control-a>', self.executeAffarsvarldenLinkScraper)
        menu.add_command(label="Execute crawl on all stored urls", command=self.executeCrawlOnAllStoredWebpages, accelerator="Ctrl+U")
        self.bind('<Control-u>', self.executeCrawlOnAllStoredWebpages)
        menu.add_separator()
        menu.add_command(label="Quit", command=self.__del__, accelerator="Ctrl+Q")
        self.bind('<Control-q>', self.__del__)
        
        try:
            self.config(menu=self.menubar)
        except AttributeError:
            self.tk.call(self, "config", "-menu", self.menubar)
        
        #tabs
        self.tabs = Pmw.NoteBook(self)
        self.tabs.pack(fill = 'both', expand = 1, padx = 5, pady = 5)
        self.tabs.add('Stock Browser')
        self.tabs.add('Stock Predictor')
        self.tabs.tab('Stock Browser').focus_set()
        
        self.tabStockBrowser = TabStockBrowser(self.tabs.page('Stock Browser'), self.db) 
        self.tabStockPredictor = TabStockPredictor(self.tabs.page('Stock Predictor'), self.db)
        
        
        self.tabs.setnaturalsize()
            
        #status bar
        self.statusBar = StatusBar(self)
        self.statusBar.pack(side=BOTTOM, fill=X)
        self.statusBar.clearText()
                
        
    def __del__(self, event=None):
        self.destroy()
 
    def executeCrawler(self, event=None):
        self.crawler.executeCrawlForStaticUrls()
    
    def executeAffarsvarldenLinkScraper(self, event=None):
        baseAddr = "http://www.affarsvarlden.se/hem/nyhetsdygnet/?sortorder=0"
        yearArg = "&year="
        monthArg = "&month="
        years = range(2010, 2012)
        months = range(1,13)
        self.crawler.clearDynamicUrls()
        for year in years:
            for month in months:
                self.crawler.addDynamicUrl(baseAddr + yearArg + str(year) + monthArg + str(month), Parser.ParserType.AFFARSVARLDEN_LINKCOLLECTION)
        self.crawler.executeCrawlForDynamicUrls()
    
    def executeCrawlOnAllStoredWebpages(self, event=None):
        links = self.db.getLinkCollection()
        self.crawler.clearDynamicUrls()
        for link, in links:
            if self.db.isLinkExisting(link) == False:
                self.crawler.addDynamicUrl(link, Parser.ParserType.AFFARSVARLDEN)
        
        self.crawler.executeCrawlForDynamicUrls()
        
    def crawlerStatusInd(self, numProcessed, numPending, isCrawlpending):
        if isCrawlpending == True:
            timeleft = self.crawler.getRateTimeLeft()
            hours = timeleft.seconds/3600
            minutes = (timeleft.seconds % 3600)/60
            seconds = (timeleft.seconds % 3600) % 60
            strTimeLeft = str(timeleft.days) + "D " + str(int(hours)) + "h" + str(int(minutes)) + "m" + str(int(seconds)) + "s"
            self.statusBar.setText("#Processed %d, Pending %d, Timeleft: %s, status:%s", numProcessed, numPending, strTimeLeft, "working")
        else:
            self.statusBar.setText("%s %d, %s %d, status:%s", "#Processed: ", numProcessed, " #Pending: ", numPending, "idle")
            
    def insertStockCsv(self):
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('comma seperated files', '.csv'), ('all files', '.*')]
        options['parent'] = self
        options['title'] = 'Open stock data'
        filename = tkFileDialog.askopenfilename(**options)
        if filename:
            dialog = Pmw.PromptDialog(self,
                                        title = 'Name your stock!',
                                        label_text = 'Stockname:',
                                        entryfield_labelpos = 'n',
                                        defaultbutton = 0,
                                        buttons = ('OK', 'Cancel'),
                                        command = self.insertStockCsvStockNamed)
            self.stocknameDialog = filename, dialog
            dialog.withdraw()
            dialog.activate()
            
    def insertStockCsvStockNamed(self, result):
        filename, dialog = self.stocknameDialog
        if result != None and result == 'OK':
            StockCsvReader( filename, self.db, dialog.get())
        dialog.deactivate(result)
        self.tabStockBrowser.listbox_stocks_populate()

  
class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def setText(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clearText(self):
        self.label.config(text="#Processed: N/A, status: idle")
        self.label.update_idletasks()


class EventloopHandler():
    def __init__(self):
        self.tkRoot = None
        
    def registerEvent(self, timeMs, callback):
        if self.tkRoot != None:
            self.tkRoot.after(timeMs, callback)