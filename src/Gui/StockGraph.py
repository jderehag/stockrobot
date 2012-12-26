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
from datetime import datetime, date
    
class StockGraph(Pmw.Blt.Graph):
    def __init__(self, master, **kwargs):
        Pmw.Blt.Graph.__init__(self, master, **kwargs)
        self.bind(sequence="<ButtonPress-3>",   func=self._mouse3Down)
        self.bind(sequence="<ButtonRelease-3>", func=self._mouse3Up  )
        self.xaxis_configure(command=self._formatXaxisLabel)
        self.yaxis_configure(command=self._formatYaxisLabel)
        self.grid_on()

    def _formatXaxisLabel(self, pathname, value):
        try:
            intValue = int(value)
            
            if intValue > 1:
                return str(datetime.fromordinal(intValue))
            else:
                return None
        except:
            return None
    
    def _formatYaxisLabel(self, pathname, value):
        try:
            floatValue = float(value)
            return str(floatValue/100)
        except:
            return None
    
###Zooming
    def _zoom(self, x0, y0, x1, y1):
        self.xaxis_configure(min=x0, max=x1)
        self.yaxis_configure(min=y0, max=y1)
    
    def _mouseDrag(self, event):
        global x0, y0, x1, y1
        (x1, y1) = self.invtransform(event.x, event.y)
             
        self.marker_configure("marking rectangle", 
            coords = (x0, y0, x1, y0, x1, y1, x0, y1, x0, y0))
        
    def _mouse3Up(self, event):
        global dragging
        global x0, y0, x1, y1
        
        if dragging:
            self.unbind(sequence="<Motion>")
            self.marker_delete("marking rectangle")
            
            if x0 <> x1 and y0 <> y1:
    
                # make sure the coordinates are sorted
                if x0 > x1: x0, x1 = x1, x0
                if y0 > y1: y0, y1 = y1, y0
                
                if event.num == 3:
                    self._zoom(x0, y0, x1, y1) # zoom in
                else:
                    (X0, X1) = self.xaxis_limits()
                    k  = (X1-X0)/(x1-x0)
                    x0 = X0 -(x0-X0)*k
                    x1 = X1 +(X1-x1)*k
                    
                    (Y0, Y1) = self.yaxis_limits()
                    k  = (Y1-Y0)/(y1-y0)
                    y0 = Y0 -(y0-Y0)*k
                    y1 = Y1 +(Y1-y1)*k
                   
                    self._zoom(x0, y0, x1, y1) # zoom out
                           
    def _mouse3Down(self, event):
        global dragging, x0, y0
        dragging = 0
        
        if self.inside(event.x, event.y):
            dragging = 1
            (x0, y0) = self.invtransform(event.x, event.y)
            
            self.marker_create("line", name="marking rectangle", dashes=(2, 2))
            self.bind(sequence="<Motion>",  func=self._mouseDrag)