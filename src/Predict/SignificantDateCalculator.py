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
from datetime import timedelta

'''
Update to somehow automatically calculate threshold?
Perhaps based on standard deviation?

Use index in the list so that we can get date values that are more relative to the number
of open days rather than specific date values (offset 7 might end up in a weekend and would therefore not exist
in a dict, but we might still have a very positive trend going on)
'''
def CalculateSignificantDates(dataList, datekey, valuekey, significanceThreshold, timedeltaList):
    significantPositiveEntries = []
    significantNegativeEntries = []
    for i in range(0, len(dataList) - 1):
        deltaListPositive = []
        for dt in timedeltaList:
            if (i + dt) < len(dataList):
                value = dataList[i][valuekey]
                deltavalue = dataList[i + dt][valuekey]
                deltaPercentage = ((deltavalue/value) - 1)*100
                if deltaPercentage >= significanceThreshold:
                    deltaListPositive.append((dt, deltavalue))                   
                #Only store sequential positive deltas 
                #(if value has gone negative in between then this is probably a non-interesting date)
                else: break
        
        deltaListNegative = []
        for dt in timedeltaList:
            if (i + dt) < len(dataList):
                value = dataList[i][valuekey]
                deltavalue = dataList[i + dt][valuekey]
                deltaPercentage = ((deltavalue/value) - 1)*100
                if deltaPercentage <= (0-significanceThreshold):
                    deltaListNegative.append((dt, deltavalue))
                #Only store sequential positive deltas 
                #(if value has gone negative in between then this is probably a non-interesting date)
                else: break 

        if len(deltaListPositive) != 0:
            assert(len(deltaListNegative) == 0)
            significantPositiveEntries.append(SignificantEntry(dataList[i], deltaListPositive))
        
        elif len(deltaListNegative) != 0:
            assert(len(deltaListPositive) == 0)
            significantNegativeEntries.append(SignificantEntry(dataList[i], deltaListNegative))
        
    return significantPositiveEntries, significantNegativeEntries 

class SignificantEntry():
    def __init__(self, elem, deltalist):
        self.elem = elem
        self.deltalist = deltalist
        
    def getWeight(self):
        # TODO
        return 1.0
        
        
        