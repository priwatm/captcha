# -*- coding: utf-8 -*-
import numpy as np
import random
import cPickle
import gzip
import matplotlib.cm as cm
import matplotlib.pyplot as plt

class Data(object):
    
    def __init__(self, verb=False):
        self.verb = verb
        self.x = {'trn': None, 'vld': None, 'tst': None}
        self.y = {'trn': None, 'vld': None, 'tst': None}
        self.s = {'trn': None, 'vld': None, 'tst': None}
        self.n = {'trn': 0,    'vld': 0,    'tst': 0}
        self.sh, self.sz = None, None
    
    def load_mnist(self, file_path):
        def vectorized_result(j):
            e = np.zeros((10, 1))
            e[j] = 1.0
            return e
    
        f = gzip.open(file_path, 'rb')
        trn_d, vld_d, tst_d = cPickle.load(f)
        f.close()
    
        self.x['trn'] = [np.reshape(x, (784, 1)) for x in trn_d[0]]
        self.y['trn'] = [vectorized_result(y) for y in trn_d[1]]
        
        self.x['vld'] = [np.reshape(x, (784, 1)) for x in vld_d[0]]
        self.y['vld'] = [vectorized_result(y) for y in vld_d[1]]
        
        self.x['tst'] = [np.reshape(x, (784, 1)) for x in tst_d[0]]
        self.y['tst'] = [vectorized_result(y) for y in tst_d[1]]
    
        self.sh = (28, 28)
        self.sz = 784
#        if len(self.sh)==1:
#            self.sh = tuple([int(np.sqrt(self.sz))]*2)
#            if np.prod(self.sh) != self.sz:
#                raise ValueError('Incorrect image unforlding.')
        for dt in self.x.iterkeys():
            self.n[dt] = len(self.x[dt])
            self.s[dt] = np.arange(0, self.n[dt], 1, dtype=int) 
        
    def random_shuffle(self, dt):
        random.shuffle(self.s[dt])
        
    def get(self, i, dt, y2int=False):
        x, y = self.x[dt][self.s[dt][i]], self.y[dt][self.s[dt][i]]
        if isinstance(y, int) and y2int==False:
            e = np.zeros((self.szy, 1), dtype=int); e[y] = 1.; y = e
        if not isinstance(y, int) and y2int==True:
            y = int(np.argmax(y))
        return x, y

    def iterate(self, dt, y2int=False):
        for i in range(self.n[dt]):
            yield self.get(i, dt, y2int)
            
    def present(self, i, dt='trn'):
        x, y = self.get(i, dt, True)
        if len(x.shape)==1 or x.shape[1]==1:
            x = x.reshape(self.sh)
        print 'Image: %s #%-d'%(dt, i),
        print '| Content: "%s"'%(unicode(y))
        plt.imshow(x, cmap=cm.Greys_r)
        plt.show()