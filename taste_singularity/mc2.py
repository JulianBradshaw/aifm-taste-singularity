import os, sys, json
import mc
from multiprocessing import get_context
F15=15.142135623730951
W=[0.3,0.5,0.7]
def k(w): return mc.me(w)/mc.BASE
_job=mc.job
def job(a):
    i,lab,lam,asym,kk,fixr=a
    if fixr: os.environ['AIFM_FIX_R']=repr(fixr)
    else: os.environ.pop('AIFM_FIX_R',None)
    mc.SC[lab]=(kk,asym)
    # patch λ
    import builtins
    r=_jobl(i,lab,lam)
    r['lam']=lam; return r
def _jobl(i,lab,lam):
    orig=mc.job.__globals__
    old=0.65
    src=mc.job
    # temporary λ override via module global
    mc.LAM=lam
    return src((i,lab))
def run(jobs,out):
    with get_context('fork').Pool(4, maxtasksperchild=50) as pool, open(out,'a') as f:
        res=[]
        for r in pool.imap_unordered(job,jobs,chunksize=2): f.write(json.dumps(r)+'\n'); f.flush(); res.append(r)
    return res
if __name__=='__main__':
    N=mc.N; OUT=mc.OUT
    ok=lambda r: 'err' not in r and r.get('m') and r.get('beta')
    ref={}
    for r in map(json.loads,open('mc300.jsonl')):
        if r['sc']=='c_w0.5_fix15' and ok(r): ref[(r['i'],0.5)]=r
    # pass 1: reference cells λ=.65, 15x for w=.3,.7
    res=run([(i,f'ref_w{w}',0.65,F15,k(w),None) for i in range(N) for w in [0.3,0.7]],OUT)
    for r in res:
        if ok(r): ref[(r['i'],float(r['sc'][5:]))]=r
    # pass 2: uncorrected w=.5 in the 3 other configs, β pinned
    cfgs=[(0.9,F15),(0.65,50.0),(0.9,50.0)]
    res=run([(i,f'raw_{lam}_{a}',lam,a,k(.5),1/ref[(i,.5)]['beta']) for i in range(N) if (i,.5) in ref for lam,a in cfgs],OUT)
    ratio={(r['i'],r['lam'],r['asym']):ref[(r['i'],.5)]['m']/r['m'] for r in res if ok(r)}
    # pass 3: corrected cells
    jobs=[]
    for i in range(N):
        for lam,a in cfgs:
            for w in W:
                if (i,w) in ref and (i,lam,a) in ratio:
                    jobs.append((i,f'cell_{lam}_{int(a)}_w{w}',lam,a,k(w)*ratio[(i,lam,a)],1/ref[(i,w)]['beta']))
    run(jobs,OUT); print('done')
