# -*- coding: utf-8 -*-
import numpy as np

class CostFunction(object):
    
    def func(self, a, y):
        pass

    def der(self, a, y):
        pass
    
class CostFunctionQuad(object):
    ''' C = 1/2 * || a - y ||^2  '''
   
    def func(self, a, y):
        return 0.5 * np.linalg.norm(a - y)**2
        
    def der(self, a, y):
        return a - y