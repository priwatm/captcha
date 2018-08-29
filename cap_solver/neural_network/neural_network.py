# -*- coding: utf-8 -*-
import time
import random
import cPickle
import numpy as np

from layer_fc import LayerFC

class NeuralNetwork(object):
    
    def __init__(self, Layers=None, verb=False):
        self.verb = verb
        self.L = 0
        self.Layers = []
        self.add_layers(Layers)
      
    def add_layers(self, Layers):
        if Layers is None:
            return
        if not isinstance(Layers, list):
            Layers = [Layers]
        self.Layers.extend(Layers)
        self.L = len(self.Layers)
        
    def set_params(self, mb_size=None, eta=None, L=None,
                   m=0, e=None, n_trn=None, n_tst=None, t=None):
        '''
        mb_size     - size of the mini-batch,
        eta         - learning rate
        L, m, e, n_trn, n_tst, t  
                    - parameters of loaded net (should not be set by user) 
        '''
        self.mb_size = mb_size
        self.eta = eta
        if L is not None:
            self.L = L
        self.m = m
        self.e = []
        if e is not None: self.e = e
        self.n_trn = []
        if n_trn is not None: self.n_trn = n_trn
        self.n_tst = []
        if n_tst is not None: self.n_tst = n_tst
        self.t = []
        if t is not None: self.t = t

    def get_params(self):
        return [self.mb_size, self.eta, self.L,
                self.m, self.e, self.n_trn, self.n_tst, self.t]
        
    def forward(self, x):
        for Layer in self.Layers:
            x = Layer.forward(x)
        return x
 
    def backward(self, x, y):
        self.Layers[-1].backward(x, y, a0=self.Layers[-2].a)
        for i in range(self.L-2, 0, -1):
            self.Layers[i].backward(x, y, 
                                    a0=self.Layers[i-1].a,
                                    W1=self.Layers[i+1].W, 
                                    e1=self.Layers[i+1].e)
    
    def update(self):
        for Layer in self.Layers[1:]:
            Layer.update(self.eta)
        
    def learning(self, X_trn, Y_trn, X_tst=None, Y_tst=None, epochs=1):
        n = X_trn.shape[1]
        inds = np.arange(n)
        for j in xrange(epochs):
            _t = time.time()
            random.shuffle(inds)
            for k in xrange(0, n, self.mb_size):
                for i in xrange(k, k+self.mb_size):
                    x = X_trn[:, inds[i]].reshape((-1, 1))
                    y = Y_trn[:, inds[i]].reshape((-1, 1))
                    self.forward(x)
                    self.backward(x, y)
                    self.m+= 1
                self.update()
            if X_tst is not None:
                err = self.check(X_tst, Y_tst)
                self.e.append(err)
                self.n_tst.append(X_tst.shape[1])
            else:
                self.e.append(None)
                self.n_tst.append(0)
            self.n_trn.append(n) 
            self.t.append(time.time()-_t)
            if self.verb:
                s = "Epoch #%3d: "%(len(self.n_trn))
                s+= "T=%8.2f; "%self.t[-1]
                s+= "m=%9d; "%self.m
                s+= "n_check=%9d; "%self.n_tst[-1]
                if self.e[-1]:
                    s+= "e_check=%-8.6f"%self.e[-1]
                print s
            
    def check(self, X_tst, Y_tst):
        n = X_tst.shape[1]
        r = 0
        for i in xrange(n):
            x = X_tst[:, i].reshape((-1, 1))
            y = np.argmax(Y_tst[:, i])
            a = np.argmax(self.forward(x))
            r+= int(a == y)
        return 1.-r*1./n
        
    def save(self, fpath):
        if fpath[-2:] != '.p':
            fpath+= '.p'
        f = open(fpath, 'wb')
        cPickle.dump(self.get_params(), f, protocol=cPickle.HIGHEST_PROTOCOL)
        f.close()
        for i in range(self.L):
            fpath_l = fpath[:-2] + '_layer%d'%i + '.p' 
            f = open(fpath_l, 'wb')
            cPickle.dump(self.Layers[i].get_params(),
                         f, protocol=cPickle.HIGHEST_PROTOCOL)
            f.close()
    
def nn_load(fpath):
    if fpath[-2:] != '.p':
        fpath+= '.p'
    NN = NeuralNetwork()
    f = open(fpath, 'rb')
    NN.set_params(*cPickle.load(f))
    f.close()
    if NN.L == 0:
        return NN
    NN.Layers = []
    for i in range(NN.L):
        fpath_l = fpath[:-2] + '_layer%d'%i + '.p' 
        f = open(fpath_l, 'rb')
        Layer = LayerFC(0, 0)
        Layer.set_params(*cPickle.load(f))
        f.close()
        NN.Layers.append(Layer)
    return NN