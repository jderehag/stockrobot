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

import sys
import pycurl
from datetime import datetime, timedelta
import Parser
import WebPage
from Crawler.Parser import ParserType


class MainCrawler():
    def __init__(self, db, eventHandler, numberOfConcurrentConnections, urls=[]):
        # We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
        # the libcurl tutorial for more info.
        try:
            import signal
            from signal import SIGPIPE, SIG_IGN
            signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        except ImportError:
            pass
        
        self.__db = db
        self.__eventHandler = eventHandler
        self.__numberOfConcurrentConnections = numberOfConcurrentConnections
        self.__isCrawlPending = False
        self.__registeredObservers = []
        self.__pendingUrlQueue = None
        self.__numProcessed = 0
        self.__staticUrls = []
        self.__dynamicUrls = []
        
        self.__totalUrls = 0
        self.__startOfExecutionStartTimestamp = datetime.now()
        self.__rate = 0
        
        for url in urls:
            url = url.strip()
            if not url or url[0] == "#":
                continue
            self.__staticUrls.append((url, ParserType.GENERIC))
        
        self.__curlMultiObj = pycurl.CurlMulti()
        self.__curlMultiObj.handles = []
        self.__freeCurlObjList = []
        self.__createAllCurlObjects()
            
    def __del__(self):
        self.__closeAllCurlObjects()
        self.__curlMultiObj.close()
        self.destroy()
           
    def __createAllCurlObjects(self):
        for i in range(self.__numberOfConcurrentConnections):
            c = pycurl.Curl()
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT, 30)
            c.setopt(pycurl.TIMEOUT, 300)
            c.setopt(pycurl.NOSIGNAL, 1)
            self.__curlMultiObj.handles.append(c)
                    
    def __closeAllCurlObjects(self):
        for c in self.__curlMultiObj.handles:
            self.__curlMultiObj.remove_handle(c)
            c.close()
        for c in self.__freeCurlObjList:    
            c.close()
            
    def registerObserver(self, observer):
        self.__registeredObservers.append(observer)
        
    def addDynamicUrl(self, url, parser):
        url = url.strip()
        if url or url[0] != "#":
            self.__dynamicUrls.append((url, parser))
    
    def clearDynamicUrls(self):
        self.__dynamicUrls = []
    
    def executeCrawlForStaticUrls(self):
        if self.__isCrawlPending == False:
            self.__isCrawlPending = True
            self.__numProcessed = 0
            self.__pendingUrlQueue = self.__staticUrls
            self.__freeCurlObjList = self.__curlMultiObj.handles[:]
            self.__markStartOfExection()
            self.__pollPendingCrawlers()
            
    def executeCrawlForDynamicUrls(self):
        if self.__isCrawlPending == False:
            self.__isCrawlPending = True
            self.__numProcessed = 0
            self.__executionStartTime = datetime.now()
            self.__pendingUrlQueue = self.__dynamicUrls
            self.__freeCurlObjList = self.__curlMultiObj.handles[:]
            self.__markStartOfExection()
            self.__pollPendingCrawlers()
            
    def getRateTimeLeft(self):
        totalLeft = self.__totalUrls - self.__numProcessed
        return timedelta(seconds=(totalLeft * self.__rate)) 
    
    def __markStartOfExection(self):
        self.__totalUrls = len(self.__pendingUrlQueue)
        self.__startOfExecutionStartTimestamp = datetime.now()
        
    def __updateRateOfExecution(self):
        timeElapsed = datetime.now() - self.__startOfExecutionStartTimestamp
        if timeElapsed.total_seconds() != 0:
            self.__rate = self.__numProcessed/timeElapsed.total_seconds()
        else:
            self.__rate = 0
        
    def __pollPendingCrawlers(self):
        # If there is an url to process and a free curl object, add to multi stack
        while self.__pendingUrlQueue and self.__freeCurlObjList:
            url, parser = self.__pendingUrlQueue.pop(0)
            webpage = WebPage.WebPage(parser, url)
            curlObj = self.__freeCurlObjList.pop()
            curlObj.filename = webpage
            curlObj.setopt(pycurl.URL, url)
            curlObj.setopt(pycurl.WRITEFUNCTION, webpage.writeBody)
            self.__curlMultiObj.add_handle(curlObj)

        # Run the internal curl state machine for the multi stack
        while 1:
            ret, num_handles = self.__curlMultiObj.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM: break
            
        # Check for curl objects which have terminated, and add them to the freelist
        while 1:                 
            num_q, ok_list, err_list = self.__curlMultiObj.info_read()
            for curlObj in ok_list:
                self.__curlMultiObj.remove_handle(curlObj)
                curlObj.filename.parse()
                if curlObj.filename.isLinkCollection():
                    self.__db.insertLinkCollection(curlObj.filename.allUrls)
                else:
                    if curlObj.filename.date != None:
                        self.__db.insertWebpage(curlObj.filename)
                    else:
                        print "DateError:", curlObj.getinfo(pycurl.EFFECTIVE_URL)
                self.__freeCurlObjList.append(curlObj)
            for curlObj, errno, errmsg in err_list:
                self.__curlMultiObj.remove_handle(curlObj)
                print "Failed: ", errno, errmsg 
                self.__freeCurlObjList.append(curlObj)
            self.__numProcessed = self.__numProcessed + len(ok_list) + len(err_list)
            
            self.__callAllStatusIndObservers()
                
            if num_q == 0:
                break
        
        self.__updateRateOfExecution()
        
        if (self.__numProcessed < len(self.__pendingUrlQueue)) or (num_handles != 0):
            self.__eventHandler.registerEvent(500,self.__pollPendingCrawlers)
        else:
            self.__isCrawlPending = False
            self.__callAllStatusIndObservers()
            
    def __callAllStatusIndObservers(self):
        for observer in self.__registeredObservers:
            observer.crawlerStatusInd(self.__numProcessed, len(self.__pendingUrlQueue) ,self.__isCrawlPending)
