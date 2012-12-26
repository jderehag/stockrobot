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
from datetime import datetime, timedelta
import re
from collections import defaultdict
word_regex = re.compile('\W+', re.UNICODE)

def SeperateWords(webpage):
    wordsDict = defaultdict(int)
    for word in word_regex.split(webpage.title):
        if word != "":
            wordsDict[word.lower()] += 1
    
    for word in word_regex.split(webpage.article):
        if word != "":
            wordsDict[word.lower()] += 1

    return wordsDict
    

class WordFrequency():
    def __init__(self, db, significantDatesPos, significantDatesNeg):
        self.__db = db
        self.__significantDatesPos = significantDatesPos
        self.__significantDatesNeg = significantDatesNeg
        self.__wordsDict = {}
        
        start = datetime.now()
        self.__webpages = self.__db.getAllWebpagesWithoutBody()
        stop = datetime.now()
        print "db query: #webpages:", len(self.__webpages), " in ", stop-start
        
        start = datetime.now()
        self.CalculateWordFrequencyTotal()
        stop = datetime.now()
        print "Frequency calculation: #words:", len(self.__wordsDict), " in ", stop-start
        
        start = datetime.now()
        self.CalculateWordFrequencyInterestingArticles()
        stop = datetime.now()
        print "Frequency calculation Interesting: #dates:", len(self.__significantDatesPos) + len(self.__significantDatesNeg), " in ", stop-start
        
    def CalculateWordFrequencyTotal(self):
        nrWebpagesFloat = float(len(self.__webpages))
        for webpage in self.__webpages:
            webpageWordDict = SeperateWords(webpage)
            for word,value in webpageWordDict.iteritems():
                if not word in self.__wordsDict:
                    wordElem = self.__createWordEntry()
                else:
                    wordElem = self.__wordsDict[word]
                    
                wordElem['nr-occurances-total'] += value
                wordElem['nr-webpages-with-occurance'] += 1
                wordElem['%-webpages-with-occurance'] = (wordElem['nr-webpages-with-occurance']/nrWebpagesFloat)*100
                self.__wordsDict[word] = wordElem    
                    
    def CalculateWordFrequencyInterestingArticles(self):
        webpagesPos = []
        webpagesNeg = []
        for elem in self.__significantDatesPos:
            dateStamp = elem.elem['date']
            webpagesPos.extend(self.__db.getWebpagesWithoutBody(dateStamp-timedelta(2), dateStamp-timedelta(1)))
        
        for elem in self.__significantDatesNeg:
            dateStamp = elem.elem['date']
            webpagesNeg.extend(self.__db.getWebpagesWithoutBody(dateStamp-timedelta(2), dateStamp-timedelta(1)))
            
        for webpage in webpagesPos:
            webpageWordDict = SeperateWords(webpage)
            for word,value in webpageWordDict.iteritems():
                if not word in self.__wordsDict:
                    wordElem = self.__createWordEntry()
                else:
                    wordElem = self.__wordsDict[word]
                wordElem['nr-pos-webpages-with-occurance'] += 1
                wordElem['%-pos-webpages-with-occurance'] = (wordElem['nr-pos-webpages-with-occurance']/float(len(webpagesPos)))*100
                self.__wordsDict[word] = wordElem

        for webpage in webpagesNeg:
            webpageWordDict = SeperateWords(webpage)
            for word,value in webpageWordDict.iteritems():
                if not word in self.__wordsDict:
                    wordElem = self.__createWordEntry()
                else:
                    wordElem = self.__wordsDict[word]
                wordElem['nr-neg-webpages-with-occurance'] += 1
                wordElem['%-neg-webpages-with-occurance'] = (wordElem['nr-neg-webpages-with-occurance']/float(len(webpagesNeg)))*100
                self.__wordsDict[word] = wordElem
                    
    def getInterestingWords(self):
        interestingWords = {}
        for word, value in self.__wordsDict.iteritems(): 
            if abs(value['%-pos-webpages-with-occurance'] - value['%-webpages-with-occurance']) > 2 and abs(value['%-pos-webpages-with-occurance'] - value['%-neg-webpages-with-occurance']) > 2:
                interestingWords[word] = value
            if abs(value['%-neg-webpages-with-occurance'] - value['%-webpages-with-occurance']) > 2 and abs(value['%-neg-webpages-with-occurance'] - value['%-pos-webpages-with-occurance']) > 2:
                interestingWords[word] = value
        return interestingWords
    
    def __createWordEntry(self):
        word = {}
        word['nr-occurances-total']             = 0
        word['nr-webpages-with-occurance']      = 0
        word['nr-pos-webpages-with-occurance']  = 0
        word['nr-neg-webpages-with-occurance']  = 0
        word['%-webpages-with-occurance']       = 0.0
        word['%-pos-webpages-with-occurance']   = 0.0
        word['%-neg-webpages-with-occurance']   = 0.0
        return word
    
    
