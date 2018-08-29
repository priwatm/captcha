# -*- coding: utf-8 -*-
COLOR_BG = 0
COLOR_FG = 1

import operator
import requests
import numpy as np
from PIL import Image
from copy import deepcopy
from StringIO import StringIO
from matplotlib import rc
rc('text', usetex=True)
rc('text.latex',unicode=True)
rc('text.latex',preamble='\usepackage[utf8]{inputenc}')
rc('text.latex',preamble='\usepackage[russian]{babel}')
import matplotlib.ticker
from matplotlib import gridspec
import matplotlib.lines as mlines
from matplotlib import pyplot as plt

class Img(object):
    
    def __init__(self, img=None, arr=None, fpath=None, url=None,
                 smb_real=None, smb_calc=None, fsmb2vec=None):
        self.smb_real = smb_real
        self.smb_calc = smb_calc
        self.fsmb2vec = fsmb2vec
        self.load(img, arr, fpath, url)

    @property
    def size(self):
        if not self.H or not self.W:
            return 0
        return self.H * self.W

    @property
    def fgnum(self):
        if not self.H or not self.W:
            return 0
        return np.sum(self.arr)

    @property
    def symb_is_corr(self):
        if self.smb_calc and self.smb_calc == self.smb_real:
            return True
        return False
        
    def clean(self):
        self.H = None
        self.W = None
        self.arr = None
        self.is_bin = False
        
    def load(self, img=None, arr=None, fpath=None, url=None):
        self.clean()
        if img is not None:
            self.arr = np.asarray(img)
        elif arr is not None:
            self.arr = arr.copy()
        elif fpath is not None:
            img = Image.open(fpath).convert('P')
            self.arr = np.asarray(img, dtype=np.int)
        elif url is not None:
            r = requests.get(url)
            img = Image.open(StringIO(r.content)).convert('P')
            self.arr = np.asarray(img)
        else:
            return          
        self.arr.setflags(write=True)
        self.H = self.arr.shape[0]
        self.W = self.arr.shape[1]
        
    def isbg(self, i, j):
        if self.arr[i, j] == COLOR_BG:
            return True
        return False
        
    def isfg(self, i, j):
        if self.arr[i, j] == COLOR_FG:
            return True
        return False
        
    def colors2bg(self, cols):
        self.colors2selected(cols, COLOR_BG)
        
    def colors2fg(self, cols):
        self.colors2selected(cols, COLOR_FG)
        
    def colors2selected(self, cols, col, icol=None):
        if not isinstance(cols, list):
            cols = [cols]
        for i in range(self.H):
            for j in range(self.W):
                if self.arr[i, j] in cols:
                    self.arr[i, j] = col
                elif icol is not None:
                    self.arr[i, j] = icol

    def binarization(self, colors_bg=None, colors_fg=None):
        self.is_bin = True
        if colors_bg is not None:
            self.colors2selected(colors_bg, COLOR_BG, COLOR_FG)
            if colors_fg is not None:
                raise ValueError('Incorrect input for binarization.')
        elif colors_fg is not None:
            self.colors2selected(colors_fg, COLOR_FG, COLOR_BG)
        else:
            raise ValueError('Incorrect input for binarization.')

    def fill_box(self, H=None, U=None, D=None, W=None, L=None, R=None, col=None):
        ''' 
        Fill by col (or by color_bg if None) all pixels (i, j) such that
        i = U, U+1, ..., D-1; j = L, L+1, ..., R-1.
        It should be 0 <= U <= D <= self.H and 0 <= L <= R <= self.W
        In pairs (H, U, D) and (W, L, R) exactly 2 values should be not None.
        '''
        if col is None:
            col = COLOR_BG
        if L is None: L = R - W
        if R is None: R = L + W
        if U is None: U = D - H 
        if D is None: D = U + H 
        for i in xrange(U, D):
            for j in xrange(L, R):
                self.arr[i, j] = col
    
    def crop(self):
        hist_fg_h, hist_fg_w = self.calc_hist_hw()
        ind = np.where(hist_fg_h != 0)[0]
        self.arr = self.arr[ind, :]
        self.H = len(ind)
        ind = np.where(hist_fg_w != 0)[0]
        self.arr = self.arr[:, ind]
        self.W = len(ind)

    def resize(self, H, W):
        if H>self.H:
            self.arr = np.vstack((np.zeros((H-self.H, self.W)), self.arr))
            self.H = H
        if W>self.W:
            self.arr = np.hstack((self.arr, np.zeros((self.H, W-self.W))))
            self.W = W

    def remove_points(self, nbg_min=4):
        for i in range(self.H):
            for j in range(self.W):
                nbg = 0
                if self.arr[i, j] == COLOR_BG:
                    continue
                if i==0 or i>0 and self.arr[i-1, j] == COLOR_BG:
                    nbg+= 1
                if i==self.H-1 or i<self.H-1 and self.arr[i+1, j] == COLOR_BG:
                    nbg+= 1
                if j==0 or j>0 and self.arr[i, j-1] == COLOR_BG:
                    nbg+= 1
                if j==self.W-1 or j<self.W-1 and self.arr[i, j+1] == COLOR_BG:
                    nbg+= 1
                if nbg >= nbg_min:
                    self.sarr[i, j] = COLOR_BG

    def get_vector_size(self, var='arr'):
        if var == 'arr':
            return self.W * self.H
        if var == 'smb_real':
            return self.fsmb2vec(self.smb_real).size
        if var == 'smb_calc':
            return self.fsmb2vec(self.smb_calc).size
        raise ValueError('Input var should be "arr" or "smb_real" or "smb_calc".')
        
    def get_vector(self, var='arr'):
        if var == 'arr':
            return self.arr.reshape((-1, 1), order='F')
        if var == 'smb_real':
            return self.fsmb2vec(self.smb_real)
        if var == 'smb_calc':
            return self.fsmb2vec(self.smb_calc)
        raise ValueError('Input var should be "arr" or "smb_real" or "smb_calc".')
        
    def calc_hist(self, present=False):          
        hist = {}
        for i in range(self.H):
            for j in range(self.W):   
                v = self.arr[i, j]
                if hist.has_key(v):
                    hist[v]+= 1
                else: 
                    hist[v] = 1      
        hist = sorted(list(hist.items()), key=operator.itemgetter(1), reverse=True)
        hist = [list(h) for h in hist]
        if present:
            self.present_hist(hist)
        return hist

    def segmentation(self, thr_h=0, thr_w=0, show=False, smbs_real=None):
        hist_fg_h, hist_fg_w = self.calc_hist_hw()

        def objs2lines(objs):
            lines = []
            for obj in objs:
                lines.append([obj[0], [obj[1][0]]*2])
                lines.append([[obj[0][1]]*2, obj[1]])
                lines.append([obj[0], [obj[1][1]]*2])
                lines.append([[obj[0][0]]*2, obj[1]])
            return lines

        def find_objs(hist, thr):
            objs = []
            in_obj = False
            for i, p in enumerate(hist):
                if not in_obj and p > thr:
                    in_obj = True
                    objs.append([i, i])
                if in_obj and p <= thr:
                    in_obj = False
                    objs[-1][1] = i
            return objs

        objs_h = find_objs(hist_fg_h, thr_h)
        objs_w = find_objs(hist_fg_w, thr_w)
        objs = [[obj_w, objs_h[0]] for obj_w in objs_w]

        from imgs import Imgs
        Ims = Imgs(fsmb2vec=self.fsmb2vec)
        for i, obj in enumerate(objs):
            arr = self.arr[obj[1][0]:obj[1][1], obj[0][0]:obj[0][1]]
            smb_real = smbs_real[i] if smbs_real and i < len(smbs_real) else None
            Im = Img(arr=arr, fsmb2vec=self.fsmb2vec, smb_real=smb_real)
            Im.is_bin = self.is_bin
            Ims.append(Im)
        if show:
            self.show_hist_hw(hist_fg_h, hist_fg_w, objs2lines(objs))
        return Ims

    def fit_to_size(self, h, w):
        dh = int((h - self.H)/2)
        dw = int((w - self.W)/2)
        arr0 = np.zeros((h, w))
        arr0[dh: self.H+dh, dw: self.W+dw] = self.arr
        self.arr = arr0
        self.H = h
        self.W = w

    def calc_hist_hw(self, show=False):
        hist_fg_h = np.sum(self.arr, axis=1)*1./COLOR_FG/self.W
        hist_fg_w = np.sum(self.arr, axis=0)*1./COLOR_FG/self.H
        if show:
            self.show_hist_hw(hist_fg_h, hist_fg_w)
        return hist_fg_h, hist_fg_w

    def copy(self):
        return deepcopy(self)

    def present(self, tostd=True):
        res = u''
        if self.smb_real is not None:
            res+= 'Real: [%s]'%self.smb_real
        if self.smb_calc is not None:
            res+= u' | Pred: [%s]'%self.smb_calc
        if tostd:
            print res
        return res
    
    def present_hist(self, hist):
        k = 0
        for i, n in hist:
            tp = ''
            if self.is_bin and i == COLOR_BG:
                tp = '(BG)'
            if self.is_bin and i == COLOR_FG:
                tp = '(FG)'
            print 'C:%3d-> %5d %-5s|'%(i, n, tp),
            if (k+1)%5==0:
                print
            k+= 1 
         
    def show_colors(self, ax=None, figsize=(7, 12), colors=COLOR_BG):
        if not isinstance(colors, list):
            colors = [colors]
        pois = []
        for i in range(self.H):
            for j in range(self.W):
                if self.arr[i, j] in colors:
                    pois.append([j, i, 'red'])
        self.show(ax, figsize, pois)

    def show(self, ax=None, figsize=(7, 12), pois=None):
        arr = self.arr.copy()
        if self.is_bin:
            for i in range(self.H):
                for j in range(self.W):
                    if arr[i, j] == COLOR_BG:
                        arr[i, j] = 255
                    if arr[i, j] == COLOR_FG:
                        arr[i, j] = 0
        sh = False
        if ax is None:
            sh = True
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        ax.imshow(arr, origin='upper', cmap='gray', vmin=0, vmax=255)
        locator = matplotlib.ticker.NullLocator()
        ax.xaxis.set_major_locator(locator)
        ax.yaxis.set_major_locator(locator)
        ax.set_title(self.present(tostd=False))
        if pois is not None:
            for poi in pois:
                plt.scatter(poi[0], poi[1], s=100, c=poi[2], marker='o')
        if sh:
            plt.show()
          
    def show_hist_hw(self, hist_fg_h, hist_fg_w, lines=None):
        gs = gridspec.GridSpec(2, 2, width_ratios=[1,1], height_ratios=[1,1])       
        axi = plt.subplot(gs[0,1])
        self.show(axi)
        if lines:
            for line in lines:
                l = mlines.Line2D(line[0], line[1]) #([xmin,xmax], [ymin,ymax])
                axi.add_line(l)
        axh = plt.subplot(gs[0,0], sharey=axi)
        axh.plot(hist_fg_h, range(self.H))   
        axw = plt.subplot(gs[1,1], sharex=axi)
        axw.plot(range(self.W), hist_fg_w)     
        plt.show()