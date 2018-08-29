# -*- coding: utf-8 -*-
import numpy as np

from act_func import ActFunctionSig
from cost_func import CostFunctionQuad

class LayerFC(object):
    
    def __init__(self, n0, n, AF=None, CF=None):
        self.n0 = n0
        self.n  = n
        self.AF = AF
        self.CF = CF
        self.clean()
        
    def set_params(self, n0, n, m, W, b):
        self.clean()
        self.n0 = n0
        self.n0 = n
        self.m = m
        self.W = W
        self.b = b

    def get_params(self):
        return [self.n0, self.n, self.m, self.W, self.b]

    def clean(self):
        if self.n0 is None: # First layer
            self.W = None
            self.b = None
        else:
            self.W = np.random.randn(self.n, self.n0)
            self.b = np.random.randn(self.n, 1)
        if self.AF is None:
            self.AF = ActFunctionSig()
        if self.CF is None:
            self.CF = CostFunctionQuad()
        self.z = None
        self.a = None
        self.m = 0
        self.dW = None
        self.db = None
        
    def forward(self, x):
        if self.W is None:
            self.z = x.copy()
            self.a = x.copy()
        else:
            self.z = self.W.dot(x) + self.b
            self.a = self.AF.func(self.z)
        return self.a
        
    def backward(self, x, y, a0, W1=None, e1=None):
        if self.W is None:
            return
        if e1 is None or W1 is None: # Last layer
            self.e = self.AF.der(self.z) * self.CF.der(self.a, y)
        else:
            self.e = self.AF.der(self.z) * (W1.T.dot(e1))
        if self.dW is None:
            self.dW = self.e.dot(a0.T)
        else:
            self.dW = self.dW + self.e.dot(a0.T)
        if self.db is None:
            self.db = self.e.copy()
        else:
            self.db = self.db + self.e
        self.m+= 1
            
    def update(self, eta): 
        if self.m <= 0:
            raise ValueError('Can not update parameters from empty data.')
        self.W = self.W - eta/self.m * self.dW
        self.b = self.b - eta/self.m * self.db
        self.dW, self.db, self.m = None, None, 0