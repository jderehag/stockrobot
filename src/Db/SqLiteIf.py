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
import sqlite3
from Crawler.WebPage import WebPage
from Crawler.Parser import ParserType
import zlib
from datetime import datetime, date
import time

def adapt_datetime(ts):
    return int(time.mktime(ts.timetuple()))
def adapt_date(ts):
    return date.toordinal(ts)
def convert_datetime(dt):
    return datetime.fromtimestamp(int(dt))
def convert_date(dt):
    return date.fromordinal(int(dt))


class SqLiteIf():
    def __init__(self, dbpath=u'../webpages.db'):
        #You can also supply the special name :memory: to create a database in RAM
        self.__conn = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
        self.__conn.text_factory = unicode
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_adapter(date, adapt_date)
        sqlite3.register_converter("DATETIME", convert_datetime)
        sqlite3.register_converter("DATE", convert_date)
    
        self.__cursor = self.__conn.cursor()
        self.createTables()

    def __del__(self):
        self.__conn.close()
    
    def getCursor(self):
        return self.__cursor
    def getConnection(self):
        return self.__conn   
        
    def createTables(self):

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS webpages
                             (date DATETIME, url text, title text, article text, body blob, PRIMARY KEY(url))''')
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS linkcollection
                         (url text, PRIMARY KEY(url))''')
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS stocknames
                         (name text, tablename text, PRIMARY KEY(name))''')
    
        self.__conn.commit()
        
    def insertWebpage(self, webpage):
        try:
            self.__cursor.execute("INSERT INTO webpages VALUES (?,?,?,?,?)", [webpage.date,
                                                                              webpage.url, 
                                                                              webpage.title,
                                                                              webpage.article, 
                                                                              buffer(zlib.compress(webpage.body))])
            self.__conn.commit()
        except sqlite3.IntegrityError:
            pass

    def getAllWebpages(self):
        self.__cursor.execute('SELECT * FROM webpages')
        webpages = []
        for dbRow in self.__cursor.fetchall():
            webpage = WebPage(ParserType.NONE, dbRow[1], dbRow[0], dbRow[2], dbRow[3], zlib.decompress(dbRow[4]))
            webpages.append(webpage)
        return webpages
    
    def getAllWebpagesWithoutBody(self):
        self.__cursor.execute('SELECT url,date,title,article FROM webpages')
        webpages = []
        for dbRow in self.__cursor.fetchall():
            webpage = WebPage(ParserType.NONE, dbRow[0], dbRow[1], dbRow[2], dbRow[3])
            webpages.append(webpage)
        return webpages
    
    def getWebpagesWithoutBody(self, dateFrom, dateTo):
        localDateFrom = datetime(*(dateFrom.timetuple()[:6]))
        localDateTo = datetime(*(dateTo.timetuple()[:6]))
        
        self.__cursor.execute('SELECT url,date,title,article FROM webpages WHERE date BETWEEN (?) AND (?) ORDER BY date ASC', (localDateFrom, localDateTo))
        webpages = []
        for dbRow in self.__cursor.fetchall():
            webpage = WebPage(ParserType.NONE, dbRow[0], dbRow[1], dbRow[2], dbRow[3])
            webpages.append(webpage)
        return webpages
        
    def getWebpages(self, dateFrom, dateTo):
        localDateFrom = datetime(*(dateFrom.timetuple()[:6]))
        localDateTo = datetime(*(dateTo.timetuple()[:6]))

        self.__cursor.execute('SELECT * FROM webpages WHERE date BETWEEN (?) AND (?) ORDER BY date ASC', (localDateFrom, localDateTo))
        webpages = []
        for dbRow in self.__cursor.fetchall():
            webpage = WebPage(ParserType.NONE, dbRow[1], dbRow[0], dbRow[2], dbRow[3], zlib.decompress(dbRow[4]))
            webpages.append(webpage)
        return webpages
                        
    def insertLinkCollection(self, links):
        for link in links:
            try:
                self.__cursor.execute("INSERT INTO linkcollection VALUES (?)", [link])
                self.__conn.commit()
            except sqlite3.IntegrityError:
                pass
    
    def getLinkCollection(self):
        self.__cursor.execute('SELECT * FROM linkcollection')
        return self.__cursor.fetchall()
    
    def isLinkExisting(self, link):
        self.__cursor.execute('SELECT 1 FROM webpages WHERE url=(?)', [link])
        if self.__cursor.fetchone() != None:
            return True
        else:
            return False
        
    def getAllStockNames(self):
        self.__cursor.execute('SELECT name FROM stocknames')
        stocknames = []
        for stockname, in self.__cursor.fetchall():
            stocknames.append(stockname)
        return stocknames
    
    def getTableNameFromStockName(self, stockname):
        self.__cursor.execute('SELECT * FROM stocknames WHERE name=(?)', [stockname])
        name, tablename = self.__cursor.fetchone() 
        return tablename
    
    def createNewStock(self, stockname):
        
        tablename = stockname.replace(" ", "_")
        try:
            self.__cursor.execute("INSERT INTO stocknames VALUES (?, ?)", [stockname, tablename])
            self.__conn.commit()
            
            self.__cursor.execute("CREATE TABLE IF NOT EXISTS " + tablename + " "  
                                  '''(date text, 
                                     shareprice_highest real, 
                                     shareprice_lowest real,  
                                     shareprice_closing real, 
                                     shareprice_average real, 
                                     totalvolume integer, 
                                     turnover integer,
                                     finishes integer, 
                                     PRIMARY KEY(date))''')
            self.__conn.commit()
        except sqlite3.IntegrityError:
            pass
        
    def insertNewStockElement(self, stockname, element):
        tablename = self.getTableNameFromStockName(stockname)
        if tablename != None:
            try:
                self.__cursor.execute("INSERT INTO " + tablename + " VALUES (?,?,?,?,?,?,?,?)", (element['date'],
                                                                                                 element['shareprice_highest'],
                                                                                                 element['shareprice_lowest'],
                                                                                                 element['shareprice_closing'],
                                                                                                 element['shareprice_average'],
                                                                                                 element['totalvolume'],
                                                                                                 element['turnover'],
                                                                                                 element['finishes']))
                self.__conn.commit()
            except sqlite3.IntegrityError:
                pass
        
    def getAllStocks(self, stockname):
        tablename = self.getTableNameFromStockName(stockname)
        if tablename != None:
            self.__cursor.execute("SELECT * FROM " + tablename + " ORDER BY date ASC")
            allStocks = {}
            for stock in self.__cursor.fetchall():
                realStock = {}
                realStock['date']                   = stock[0]
                realStock['shareprice_highest']     = stock[1]  
                realStock['shareprice_lowest']      = stock[2]
                realStock['shareprice_closing']     = stock[3]
                realStock['shareprice_average']     = stock[4]
                realStock['totalvolume']            = stock[5]
                realStock['turnover']               = stock[6]
                realStock['finishes']               = stock[7]
                allStocks[realStock['date']] = realStock
            return allStocks
        else:
            return None
        
        
        