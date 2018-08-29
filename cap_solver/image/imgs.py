# -*- coding: utf-8 -*-
import os
import gzip
import time
import random
import cPickle
import numpy as np

from matplotlib import rc
rc('text', usetex=True)
rc('text.latex', unicode=True)
rc('text.latex', preamble='\usepackage[utf8]{inputenc}')
rc('text.latex', preamble='\usepackage[russian]{babel}')
from matplotlib import pyplot as plt

from img import Img

class Imgs(list):
    
    def __init__(self, fsmb2vec=None, verb=False):
        super(Imgs, self).__init__()
        self.fsmb2vec = fsmb2vec
        self.verb = verb

    @property
    def len_(self):
        return len(self)
        
    def load(self, fpath, num=None, rand=False, dtype='folder'):
        _t = time.time()
        if dtype == 'folder':
            self.load_from_folder(fpath, num, rand)
        elif dtype == 'mnist':
            self.load_from_mnist_zip(fpath, num, rand)
        else:
            raise ValueError('Input dtype should be "folder" of "mnist".')
        _t = time.time() - _t
        if self.verb:
            print 'Total time   (sec.): %6.1f'%_t
            print 'Time per img (sec.): %9.4f'%(_t/self.len_)
            print 'Total number of img: %9d'%self.len_
            
    def load_from_mnist_zip(self, fpath, num=None, rand=False):
        f = gzip.open(fpath, 'rb')
        trn_d, vld_d, tst_d = cPickle.load(f)
        f.close()
        x_d = np.vstack((trn_d[0], vld_d[0], tst_d[0]))
        y_d = np.hstack((trn_d[1], vld_d[1], tst_d[1]))
        nums_all = np.arange(len(x_d))
        for i in xrange(len(x_d)):
            if rand:
                j = random.choice(nums_all)
            else:
                j = i
            x = x_d[j].reshape((28, 28))*256
            y = unicode(y_d[j])
            Im = Img(arr=x, smb_real=y, fsmb2vec=self.fsmb2vec)
            self.append(Im)
            if num and self.len_ >= num:
                break
                
    def load_from_folder(self, fpath, num=None, rand=False):
        for path, dirs, files in os.walk(fpath):
            nums_all = np.arange(len(files))
            for i in xrange(len(files)):
                if rand:
                    fname = files[random.choice(nums_all)]
                else:
                    fname = files[i]
                if fname.startswith('.'):
                    continue
                fpath = os.path.join(path, fname)
                value = unicode(fname.split('.')[0].decode('utf-8'))
                Im = Img(fpath=fpath, smb_real=value, fsmb2vec=self.fsmb2vec)
                self.append(Im)
                if num and self.len_ >= num:
                    break

    def get_matrix(self, var='arr', n=None, n_trn=None, n_vld=None):
        if self.len_ <= 0:
            raise ValueError('Empty list of images.')
        m = self[0].get_vector_size(var)
        if n is None:
            n = self.len_
        X = np.zeros((m, n))
        for j in xrange(n):
            X[:, j] = self[j].get_vector(var)[:, 0]
        if n_trn is not None:
            X = [X[:, :n_trn], X[:, n_trn:]]
        if n_vld is not None:
            X = [X[0], X[1][:, :n_vld], X[2][:, n_vld:]]
        return X

    def copy(self, nums=None):
        if nums is None:
            nums = np.arange(self.len_)
        Ims = Imgs(fsmb2vec=self.fsmb2vec, verb=self.verb)
        for num in nums:
            Ims.append(self[num].copy())
        return Ims
        
    def apply(self, func, use_arr=False, res_arr=False):
        _t = time.time()
        for q, Im in enumerate(self):
            _t_st = time.time()
            if use_arr:
                res = func(Im.arr)
                if res_arr:
                    Im.arr = res
            else:
                func(Im)
            _t_st = time.time() - _t_st
            _t_fl = time.time() - _t
            if self.verb and (q%10==0 or q == self.len_-1):
                print '\rPrepared: %8d / %8d | T_loop=%-7.4f s., T_full=%-7.1f s., T_rem=%-7.1f s.'%\
                      (q+1, self.len_, _t_st, _t_fl, _t_fl*(self.len_-q-1)*1./(q+1)),
        if self.verb:
            print
            print 'Total time   (sec.): %6.1f'%(time.time() - _t)
            print 'Time per img (sec.): %9.4f'%((time.time() - _t)/self.len_)
       
    def show(self, n=None, r=None, c=None, 
             figsize=(7, 12), figsize_sub=(7, 12), fsave=None):
        show(self, n, r, c, figsize, figsize_sub, fsave)
        
def show(Ims, n=None, r=None, c=None, 
         figsize=(7, 12), figsize_sub=(7, 12), fsave=None):
    if n is None:
        n = len(Ims)
    if n < 1:
        return
    if r is None and c is None: 
        r = 1; c = n
    elif r is None: 
        r = n/c
    elif c is None: 
        c = n/r
    fig, axs = plt.subplots(nrows=r, ncols=c, figsize=figsize) 
    plt.subplots_adjust(wspace=0.2, hspace=0.2)
    if r==1 and c==1:
        axs = np.array([[axs]])
    elif r==1:
        axs = axs.reshape((1, -1))
    elif c==1:
        axs = axs.reshape((-1, 1))
    for i in xrange(r):
        for j in xrange(c):
            m = j + c*i
            Ims[m].show(axs[i][j], figsize_sub)
    if fsave:
        fig.savefig(fsave, bbox_inches='tight')
    plt.show()