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
import csv

def convertToFloat(string):
    if string != "":
        return float(string.replace(" ", "").replace(",", "."))
    else:
        return 0.0

def convertToInt(string):
    if string != "":
        return int(string.replace(" ", ""))
    else:
        return 0
    

class StockCsvReader():
    def __init__(self, filename, db, stockname):
        with open(filename, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, 
                                     fieldnames=['date',
                                                 'shareprice_highest',
                                                 'shareprice_lowest',  
                                                 'shareprice_closing',
                                                 'shareprice_average', 
                                                 'totalvolume', 
                                                 'turnover',
                                                 'finishes'] 
                                     ,dialect='excel')
        
        
            db.createNewStock(stockname)
            for row in reader:
                if row['date'] != "Datum":
                    element = {}
                    element['date'] = str(row['date'])
                    element['shareprice_highest'] = convertToFloat(row['shareprice_highest'])
                    element['shareprice_lowest'] = convertToFloat(row['shareprice_lowest'])  
                    element['shareprice_closing'] = convertToFloat(row['shareprice_closing'])
                    element['shareprice_average'] = convertToFloat(row['shareprice_average'])
                    
                    element['totalvolume'] = convertToInt(row['totalvolume'])
                    element['turnover'] = convertToInt(row['turnover'])
                    element['finishes'] = convertToInt(row['finishes'])
                    db.insertNewStockElement(stockname, element)
        
    