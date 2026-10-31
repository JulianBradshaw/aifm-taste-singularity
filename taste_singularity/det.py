import tos, json, numpy as np
from concurrent.futures import ProcessPoolExecutor
BASE=0.2409892194931128; S0=2.1
def withm(mt, asym, extra={}):
    s=S0*mt/BASE
    for _ in range(4):
        r=tos.go(dict({'parallel_penalty':0.65,'ai_research_taste_slope':s,'inf_labor_asymptote':asym},**extra))
        if r.get('m') is None: return r
        if abs(r['m']-mt)<1e-4: break
        s*=mt/r['m']
    r['slope_in']=s; return r
def job(a):
    lab,mt,asym=a; r=withm(mt,asym); r['lab']=lab; r['mt']=mt; r['asym']=asym; return r
if __name__=='__main__':
    ms=0.615; md=0.24
    meff=lambda w: w*md+(1-w)*ms
    J=[('a default',BASE,15.142135623730951),('b TasteVal',ms,15.142),('c w=.3',meff(.3),15.142),('c w=.5',meff(.5),15.142),('c w=.7',meff(.7),15.142),
       ('d w=.5 50x',meff(.5),50),('e w=.5 unb',meff(.5),1e5),('a default 50x',BASE,50),('a default unb',BASE,1e5)]
    with ProcessPoolExecutor(8) as ex: out=list(ex.map(job,J))
    json.dump(out,open('det.json','w'),indent=0)
    for r in out: print(r['lab'], {k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items() if k not in('lab','keys')})
