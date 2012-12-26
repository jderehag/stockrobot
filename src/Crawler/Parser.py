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
from bs4 import BeautifulSoup
import re
import datetime, time

USE_PARSER="lxml"
timeCompRegex = re.compile('\d?:\d?')

class ParserType():
    NONE = 'NONE'
    GENERIC = 'GENERIC'
    AFFARSVARLDEN='AFFARSVARLDEN'
    AFFARSVARLDEN_LINKCOLLECTION='AFFARSVARLDEN_LINKCOLLECTION'

class ParserAffarsVarldenLinkCollector():
    def __init__(self, webpage):
        self.__soup = BeautifulSoup(webpage, USE_PARSER)
    
    def getText(self):
        return self.__soup.get_text()
        
    def getAllUrls(self):
        links = []
        for link in self.__soup.find_all('a', href=re.compile("http://www.affarsvarlden.se/hem/nyheter/article.*ece$")):
            links.append(link.get('href'))
        return links
        
    def getDate(self):
        return None
    
    def getTitle(self):
        return None
    
    def getArticle(self):
        return None
   
class ParserAffarsVarlden():
    def __init__(self, webpage):
        self.__soup = BeautifulSoup(webpage, USE_PARSER)
    
    def getText(self):
        return self.__soup.get_text()
        
    def getAllUrls(self):
        links = []
        for link in self.__soup.find_all('a', href=re.compile("http://www.affarsvarlden.se/hem/nyheter/article")):
            links.append(link)
        return links
        
    def getDate(self):
        tag = self.__soup.find('p', class_="dateline")
        if tag != None:
            for strings in tag.stripped_strings:
                date = DateTimeParse().Parse(strings)
                if date != None:
                    return date
            print "dateline:", tag.stripped_strings
        return None
    
    def getTitle(self):
        return self.__soup.title.string.strip().replace(u" - Affärsvärlden", "").capitalize()
    
    def getArticle(self):
        article = "" 
        tag = self.__soup.find('p', class_="lead")
        if tag != None:
            for string in tag.stripped_strings:
                article += string + "\n"
        tag = self.__soup.find('div', class_="article-bread")
        if tag != None:
            for string in tag.stripped_strings:
                article += string + "\n" 
        return article 
        
        
class ParserGeneric():
    def __init__(self, webpage):
        self.__soup = BeautifulSoup(webpage, USE_PARSER)
    
    def getText(self):
        return self.__soup.get_text()
        
    def getAllUrls(self):
        links = []
        for link in self.__soup.find_all('a'):
            links.append(link.get('href'))
        return links
        
    def getDate(self):
        return
    
    def getTitle(self):
        return
    
    def getArticle(self):
        return


class DateTimeParse():
    __MonthNames = {'januari':   1,
                    'january':   1,
                    'jan':       1,

                    'februari':  2,
                    'february':  2,
                    'feb':       2,
                   
                    'mars':      3,
                    'march':     3,
                    'mar':       3,
                   
                    'april':     4,
                    'apr':       4,
                   
                    'maj':       5,
                    'may':       5,
                   
                    'juni':      6,
                    'june':      6,
                    'jun':       6,
                    
                    'juli':      7,
                    'july':      7,
                    'jul':       7,
                   
                    'augusti':   8,
                    'august':    8,
                    'aug':       8,
                    
                    'september': 9,
                    'sep':       9,
                    
                    'oktober':   10,
                    'okt':       10,
                    
                    'november':  11,
                    'nov':       11,
                    
                    'december':  12,
                    'dec':       12}
    
    def Parse(self, datestring):
        year = None    
        month = None
        day = None
        timeStamp = None
        for component in datestring.strip().split():

            # Try year
            try:
                yearCandidate = int(component)
                if 1900 < yearCandidate < 3000:
                    year = yearCandidate
                    continue
            except ValueError:
                pass
                     
            # Try Month              
            try:
                month = DateTimeParse.__MonthNames[component.lower()]
                continue
            except KeyError:
                pass

            #try day
            try:
                dayCandidate = int(component)
                if 1 <= yearCandidate <= 31:
                    day = dayCandidate
                    continue
            except ValueError:
                pass
        
            #Try time
            try:
                timeStamp = time.strptime(component, "%H:%M")
                continue
            except ValueError:
                pass
            
                        # try today
            if "today" or "idag" in component.lower():
                today = datetime.date.today()
                year = today.year
                month = today.month
                day = today.day
                continue
    
        if(year != None and month != None and day != None and timeStamp != None):
            return datetime.datetime(year, month, day, timeStamp.tm_hour, timeStamp.tm_min)
        else:
            return None
        
    
        