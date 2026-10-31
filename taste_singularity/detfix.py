import os, sys
os.environ['AIFM_FIX_R']='3.060457817866595'
import det
from concurrent.futures import ProcessPoolExecutor
ms=0.615; md=0.24; me=lambda w: w*md+(1-w)*ms
J=[('a default 15x',det.BASE,15.142),('d w=.5 50x fixβ',me(.5),50),('e w=.5 unb fixβ',me(.5),1e5),('a default 50x fixβ',det.BASE,50),('a default unb fixβ',det.BASE,1e5),('b TasteVal unb fixβ',ms,1e5),('c w=.7 unb fixβ',me(.7),1e5)]
if __name__=='__main__':
    with ProcessPoolExecutor(3) as ex: out=list(ex.map(det.job,J))
    for r in out: print(r['lab'], 'm/b',round(r['m']/r['beta'],3), 'beta',round(r['beta'],3),'AC',round(r['ac'],2),'ASI',round(r['asi'],2),'tk',round(r['takeoff'],2))
