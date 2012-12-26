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
import Pmw
import numpy
from MultiListbox import MultiListbox
from StockGraph import StockGraph
from datetime import datetime, date, timedelta

import webbrowser


def StockHistogram_formatXaxisLabel(pathname, value):
    try:
        intValue = int(value)
        if(intValue < 365):
            return str(value) + "d"
        else:
            strValue = str(int(intValue/365)) + "y" + str(intValue%365) + "d"
            return strValue
    except:
        return None
            
class TabStockBrowser():
    def __init__(self, frame, db):
        self.frame = frame
        self.__db = db
        
        self._histogramRange = (10*365)
        
        self.histogram_stock = Pmw.Blt.Graph(self.frame, height=100)
        self.histogram_stock.xaxis_configure(stepsize=self._histogramRange/20, command=StockHistogram_formatXaxisLabel)
        self.histogram_stock.grid_on()
        self.histogram_stock.pack(side=BOTTOM, anchor=S, fill=X)
        
        self.graph_stock = StockGraph(self.frame, height=200)
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
        
        self.listBox_webpages = MultiListbox(self.frame, 'Webpages:', (('Date', 10), ('Title', 40))) 
        self.listBox_webpages.bind("<Double-Button-1>", self.listBox_webpagesDoubleClick)
        self.listBox_webpages.pack(side=LEFT,anchor=W, fill=BOTH, expand=YES)    
        
        self.listbox_stocks_populate()

    def listbox_stocks_populate(self):
        self._allStockNames = self.__db.getAllStockNames()
        self.listbox_stocks.setlist(self._allStockNames)
    
    def graph_stock_populate(self, stockname):
        self.__allStocks = self.__db.getAllStocks(stockname)

        vector_x = []
        vector_y = []
        for stock in sorted(self.__allStocks.itervalues()):
            vector_x.append(stock['date'].toordinal())
            vector_y.append(int(stock['shareprice_closing']*100))

        self.graph_stock.line_create(stockname, xdata=vector_x, ydata=vector_y, symbol='')
        self.graph_stock.legend_configure(self.graph_stock.legend_get(0), hide=True)
        

        (nValues, bins) = numpy.histogram(vector_y, bins=range(self._histogramRange))
        
        # filter out small numbers so that trimming is fairly efficient
        numpy.putmask(nValues, nValues<=3, 0)
        trimmedN = numpy.trim_zeros(nValues)
        histvector_x = bins.astype(int)[0:len(trimmedN)].tolist()
        histvector_y = trimmedN.astype(int).tolist()

        self.histogram_stock.bar_create(stockname, xdata=histvector_x, ydata=histvector_y, barwidth=3.0)
        self.histogram_stock.legend_configure(self.histogram_stock.legend_get(0), hide=True)
    
    def populate_webpages(self, stock):
        self.listBox_webpages.delete(0, END)
        self._selectedWebpages = self.__db.getWebpages(stock['date']-timedelta(3), stock['date'])
        for webpage in self._selectedWebpages:
            self.listBox_webpages.insert(END, (str(webpage.date), str(webpage.title)))
        
    def listbox_stocks_SingleClick(self):
        stockname = self._allStockNames[int(self.listbox_stocks.curselection()[0])]
        self.graph_stock_populate(stockname)
    
    def listBox_webpagesDoubleClick(self, event):
        webpage = self._selectedWebpages[int(self.listBox_webpages.curselection()[0])]
        webbrowser.open(webpage.url, new=0, autoraise=True)
    
    def graph_stock_mouseSelect(self, event):
        dicto = self.graph_stock.element_closest(event.x, event.y, halo=1000, interpolate=0)
        if dicto != None:
            stock = self.__allStocks[date.fromordinal(int(dicto['x']))]
            labelText = "StockEntry: " + str(stock['date']) + " value: " + str(stock['shareprice_closing']) + " SEK"
            self.label_graph_stock.config(text=labelText)
            
            (Y0, Y1) = self.graph_stock.yaxis_limits()
            self.graph_stock.marker_create("line", name="marking line", dashes="", linewidth=2,
                                              coords=(dicto['x'], Y0, dicto['x'], Y1))
            self.populate_webpages(stock)
        


        