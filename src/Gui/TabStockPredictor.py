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
from StockGraph import StockGraph
import Pmw
from MultiListbox import MultiListbox
from datetime import datetime, date, timedelta
from Predict import WordFrequency, SignificantDateCalculator

interestDatesThreshold = 3 #Threshold in percent
interestingDatesTimeDeltaList = [1,2,3,7] #deltadates in offset index (not actual days)

class TabStockPredictor():
    def __init__(self, frame, db):
        self.frame = frame
        self.__db = db
        self.__allStocks = {}       
        self.__selectedStock = None
        
        self.graph_stock = StockGraph(self.frame, height=100)
        self.graph_stock.bind(sequence="<ButtonPress-1>",   func=self.graph_stock_mouseSelect)
        self.graph_stock.pack(side=BOTTOM, anchor=S, fill=X)
        
        self.label_graph_stock = Label(self.frame, text="StockEntry:")
        self.label_graph_stock.pack(side=BOTTOM, anchor=SW)
        
        self.listbox_stocks = Pmw.ScrolledListBox(self.frame,
                                                  labelpos='nw',
                                                  label_text='Stocks:',
                                                  usehullsize=1,
                                                  hull_width=200,
                                                  vscrollmode='static',
                                                  selectioncommand=self.listbox_stocks_SingleClick)
        
        self.listbox_stocks.pack(side=LEFT, anchor=W, fill=Y, padx=5, pady=5)
        self.listbox_stocks_populate()
        
        #tabs
        self.tabs = Pmw.NoteBook(self.frame)
        self.tabs.pack(fill = 'both', expand = 1, padx = 5, pady = 5)
        self.tabs.add('word-frequency')
        self.tabs.tab('word-frequency').focus_set()
        
        self.tabWordFreq = TabPredictWordFreq(self.tabs.page('word-frequency'), self.__db) 
        
        

    def listbox_stocks_populate(self):
        self._allStockNames = self.__db.getAllStockNames()
        self.listbox_stocks.setlist(self._allStockNames)
        
    def listbox_stocks_SingleClick(self):
        self.__selectedStock = self._allStockNames[int(self.listbox_stocks.curselection()[0])]
        self.tabWordFreq.setSelectedStock(self.__selectedStock)
        self.graph_stock_populate(self.__selectedStock)
        
        
    def graph_stock_populate(self, stockname):
        self.__allStocks = self.__db.getAllStocks(stockname)

        vector_x = []
        vector_y = []
        for stock in sorted(self.__allStocks.itervalues()):
            vector_x.append(stock['date'].toordinal())
            vector_y.append(int(stock['shareprice_closing']*100))

        self.graph_stock.line_create(stockname, xdata=vector_x, ydata=vector_y, symbol='')
        self.graph_stock.legend_configure(self.graph_stock.legend_get(0), hide=True)
             
    def graph_stock_mouseSelect(self, event):
        dicto = self.graph_stock.element_closest(event.x, event.y, halo=1000, interpolate=0)
        if dicto != None:
            stock = self.__allStocks[date.fromordinal(int(dicto['x']))]
            labelText = "StockEntry: " + str(stock['date']) + " value: " + str(stock['shareprice_closing']) + " SEK"
            self.label_graph_stock.config(text=labelText)
            
            (Y0, Y1) = self.graph_stock.yaxis_limits()
            self.graph_stock.marker_create("line", name="marking line", dashes="", linewidth=2,
                                              coords=(dicto['x'], Y0, dicto['x'], Y1))


class TabPredictWordFreq(Frame):
    def __init__(self, parentFrame, db, **kwargs):
        Frame.__init__(self, parentFrame, **kwargs)
        self.parent = parentFrame
        self.__db = db
        self.__selectedStock = None
        
        Button(parentFrame, text="Calculate", command=self.calculate_wordFrequencies).pack()
        self.listBox_words = MultiListbox(parentFrame, None, (('word', 20), ('Occ. Total', 20), ('% total', 20), ('% Pos', 20), ('% Neg', 20)))
        self.listBox_words.pack(side=LEFT,anchor=W, fill=BOTH, expand=YES)
    
    def calculate_wordFrequencies(self):
        if self.__selectedStock != None:
            start = datetime.now()
            allStocks = self.__db.getAllStocks(self.__selectedStock)
            stop = datetime.now()
            print "db query getAllStocks: #stockentries:", len(allStocks), " in ", stop-start
            
            start = datetime.now()
            pos, neg = SignificantDateCalculator.CalculateSignificantDates(sorted(allStocks.itervalues()), 
                                                                                     'date', 
                                                                                     'shareprice_closing',
                                                                                      interestDatesThreshold, 
                                                                                      interestingDatesTimeDeltaList)
            stop = datetime.now()
            print "calculate significant dates: #stockentries:", len(pos) + len(neg), " in ", stop-start
            
            
            wf = WordFrequency.WordFrequency(self.__db, pos, neg)
            words = wf.getInterestingWords()
            
            start = datetime.now()
            self.listBox_words.delete(0, END)
        
            for word in sorted(words, key=words.get, reverse=True):
                self.listBox_words.insert(END, 
                                          (word, 
                                           words[word]['nr-webpages-with-occurance'], 
                                           "{0:.2f}".format(words[word]['%-webpages-with-occurance']), 
                                           "{0:.2f}".format(words[word]['%-pos-webpages-with-occurance']),
                                           "{0:.2f}".format(words[word]['%-neg-webpages-with-occurance'])))
            stop = datetime.now()
            print "populate listbox: #words:", len(words), " in ", stop-start
            
        
    def setSelectedStock(self, stock):
        self.__selectedStock = stock
        