#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-
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
from Db import SqLiteIf
import Crawler
import zlib
from datetime import datetime

def getAllWebpagesWithStmt(cursor, stmt):
        cursor.execute(stmt)
        webpages = []
        faultyWebpages = []
        for dbRow in cursor.fetchall():
            try:
                webpage = Crawler.WebPage.WebPage(Crawler.Parser.ParserType.NONE, dbRow[1], dbRow[0], dbRow[2], dbRow[3], zlib.decompress(dbRow[4]))
                webpages.append(webpage)
            except zlib.error:
                faultyWebpages.append(dbRow[1])
                continue
        return webpages, faultyWebpages
    
if __name__ == '__main__': 
##    newDb = SqLiteIf.SqLiteIf('webpages_new.db')
    oldDb = SqLiteIf.SqLiteIf('webpages.db') 
    total = 0
    for year in range(1998, 2013):
        wp = oldDb.getWebpages(datetime(year,1,1), datetime(year,12,31))
        print year, " ", len(wp)
        total += len(wp)
    print "Total:", total
        
    

    
'''                    
    ### handle all stocks
    for stockname in oldDb.getAllStockNames():         
        newDb.createNewStock(stockname)
        allStocks = oldDb.getAllStocks(stockname)
        for stockElement in allStocks:
            newDb.insertNewStockElement(stockname, stockElement)
    
    ### Handle webpages
    webpages = oldDb.getAllWebpages()
    print "Found ", len(webpages), " webpages"
    i = 0
    for webpage in webpages:
        i += 1
        if i % 100 == 0:
            print "inserted ", i, " webpages of ", len(webpages)
        newDb.insertWebpage(webpage)

        
    ### Handle linkcollection    
    newDb.insertLinkCollection(oldDb.getLinkCollection())   
'''

