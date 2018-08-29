# -*- coding: utf-8 -*-
from numba import jit

@jit(nopython=True)
def thinning_check(p, ch, step=1):
    if not p:
        return False
    B = 0
    for c in ch:
        B+= c
    if B < 2 or B > 6:
        return False
 
    A = 0
    for c1, c2 in zip(ch, ch[1:] + [ch[0]]):
        if c1 == 0 and c2 == 1:
            A+= 1           
    if not A == 1:
        return False
    
    if step == 1 and not ch[0] * ch[2] * ch[4] == 0:
        return False

    if step == 1 and not ch[2] * ch[4] * ch[6] == 0:
        return False
    
    if step == 2 and not ch[0] * ch[2] * ch[7] == 0:
        return False

    if step == 2 and not ch[0] * ch[4] * ch[6] == 0:
        return False
    
    return True

@jit(nopython=True)
def thinning(arr):
    while 1>0:
        found = False
        for step in [1, 2]:
            pois = []
            for i in range(1, arr.shape[0]-1):
                for j in range(1, arr.shape[1]-1):
                    ch = [arr[i-1, j], arr[i-1, j+1], arr[i, j+1], arr[i+1, j+1], 
                          arr[i+1, j], arr[i+1, j-1], arr[i, j-1], arr[i-1, j-1]]
                    if thinning_check(arr[i, j], ch, step):
                        pois.append((i, j))          
            for p in pois:
                found = True
                arr[p] = 0
        if not pois:
            break
    return arr

@jit(nopython=True)
def denoizing(arr):
    count = 0
    for i in xrange(1, arr.shape[0]-1):
        for j in xrange(1, arr.shape[1]-1):
            if not arr[i, j] == 1:
                continue
            B = 0
            for i1 in [i-1, i, i+1]:
                for j1 in [j-1, j, j+1]:
                    if arr[i1, j1] == 1:
                        B+= 1
            ok = False
            if B < 3:
                ok = True
            elif B == 3 and arr[i, j+1] == 1 and arr[i+1, j+1] == 1:
                ok = True
            elif B == 3 and arr[i, j+1] == 1 and arr[i-1, j+1] == 1:
                ok = True
            elif B == 3 and arr[i-1, j] == 1 and arr[i-1, j-1] == 1:
                ok = True   
            elif B == 3 and arr[i, j-1] == 1 and arr[i-1, j-1] == 1:
                ok = True  
            elif B == 3 and arr[i, j-1] == 1 and arr[i-1, j] == 1:
                ok = True    
            elif B == 3 and arr[i, j-1] == 1 and arr[i+1, j-1] == 1:
                ok = True  
            elif B == 3 and arr[i, j-1] == 1 and arr[i+1, j] == 1:
                ok = True  
            elif B == 3 and arr[i+1, j] == 1 and arr[i+1, j+1] == 1:
                ok = True   
            elif B == 4 and arr[i-1, j-1] == 1 and arr[i-1, j] == 1 and arr[i, j-1] == 1:
                ok = True   
            elif B == 4 and arr[i-1, j] == 1 and arr[i-1, j+1] == 1 and arr[i, j+1] == 1:
                ok = True   
            if ok:
                count+= 1
                arr[i, j] = 0
                
@jit(nopython=True)
def thinning0(arr):
    count = 0
    for i in xrange(1, arr.shape[0]-1):
        for j in xrange(1, arr.shape[1]-1):
            if not arr[i, j] == 1:
                continue
            B = 0
            for i1 in [i-1, i, i+1]:
                for j1 in [j-1, j, j+1]:
                    if arr[i1, j1] == 1:
                        B+= 1
            B-= 1
            if not (B >= 2 and B <= 6):
                continue
            
            A = 0
            pl = [arr[i-1, j], arr[i-1, j+1], arr[i, j+1], arr[i+1, j+1],
                  arr[i+1, j], arr[i+1, j-1], arr[i, j-1], arr[i-1, j-1]]
            for i1 in range(8):
                if pl[i1] == 1 and pl[i1-1] == 0:
                    A+= 1
            if not (A == 1):
                continue

            if not (arr[i-1, j] * arr[i, j+1] * arr[i+1, j] == 0):
                continue

            if not (arr[i, j+1] * arr[i+1, j] * arr[i, j-1] == 0):
                continue
                
            count+= 1
            arr[i, j] = 0
            
    for i in xrange(1, arr.shape[0]-1):
        for j in xrange(1, arr.shape[1]-1):
            if not arr[i, j] == 1:
                continue
            B = 0
            for i1 in [i-1, i, i+1]:
                for j1 in [j-1, j, j+1]:
                    if arr[i1, j1] == 1:
                        B+= 1
            B-= 1
            if not (B >= 2 and B <= 6):
                continue
            
            A = 0
            pl = [arr[i-1, j], arr[i-1, j+1], arr[i, j+1], arr[i+1, j+1],
                  arr[i+1, j], arr[i+1, j-1], arr[i, j-1], arr[i-1, j-1]]
            for i1 in range(8):
                if pl[i1] == 1 and pl[i1-1] == 0:
                    A+= 1
            if not (A == 1):
                continue

            if not (arr[i-1, j] * arr[i, j+1] * arr[i, j-1] == 0):
                continue
                
            if not (arr[i-1, j] * arr[i+1, j] * arr[i, j-1] == 0):
                continue
                
            count+= 1
            arr[i, j] = 0
