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
import datetime
import Parser

class WebPage():
    def __init__(self, parserType, url, date=None, title=u"", article=u"", body=u""):
        self.url = url
        self.parserType = parserType
        self.title = title
        self.article = article
        self.body = body
        self.allUrls = []
        self.date = date
        
    def writeBody(self, body):
        if body != None:
            self.body += body
    
    def parse(self):
        assert self.parserType != Parser.ParserType.NONE
        
        if self.parserType == Parser.ParserType.GENERIC:
            parser = Parser.ParserGeneric(self.body)
        elif self.parserType == Parser.ParserType.AFFARSVARLDEN:
            parser = Parser.ParserAffarsVarlden(self.body)
        elif self.parserType == Parser.ParserType.AFFARSVARLDEN_LINKCOLLECTION:
            parser = Parser.ParserAffarsVarldenLinkCollector(self.body)
            
        self.allUrls = parser.getAllUrls()
        self.date = parser.getDate()
        self.title = parser.getTitle()
        self.article = parser.getArticle()
        
    def isLinkCollection(self):
        if self.parserType == Parser.ParserType.AFFARSVARLDEN_LINKCOLLECTION:
            return True
        else: 
            return False
