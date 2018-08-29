# -*- coding: utf-8 -*-
import numpy as np

class ActFunction(object):
    
    def func(self, z):
        pass

    def der(self, z):
        pass
    
class ActFunctionSig(ActFunction):
    """ Sigmoid function f(z) = 1 / (1 + e^(-z))  """
    
    def func(self, z):
        return 1. / (1. + np.exp(-z))
    
    def der(self, z):
        f = self.func(z)
        return f * (1. - f)