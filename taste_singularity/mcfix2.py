import os, json, mc
A={r['i']:r for r in map(json.loads,open('mc300.jsonl')) if r['sc']=='c_w0.5_fix15' and 'err' not in r}
B={(r['i'],r['sc']):r for r in map(json.loads,open('mcfix.jsonl')) if 'err' not in r}
mc.SC.update({'d_fixbm_50x':(None,50.0),'e_fixbm_unb':(None,1e5)})
_job=mc.job
def job(a):
    i,sc=a; src={'d_fixbm_50x':'d_fixb_50x','e_fixbm_unb':'e_fixb_unb'}[sc]
    if i not in A or (i,src) not in B: return dict(i=i,sc=sc,err='nobase')
    os.environ['AIFM_FIX_R']=repr(1/A[i]['beta'])
    # k relative to sampled slope: used slope in B was sampled*k0; correct by mA/mB
    k0=mc.me(.5)/mc.BASE
    mc.SC[sc]=(k0*A[i]['m']/B[(i,src)]['m'], mc.SC[sc][1])
    return _job(a)
if __name__=='__main__':
    from multiprocessing import get_context
    jobs=[(i,sc) for i in range(mc.N) for sc in ['d_fixbm_50x','e_fixbm_unb']]
    with get_context('fork').Pool(4, maxtasksperchild=50) as pool, open(mc.OUT,'w') as f:
        for r in pool.imap_unordered(job,jobs,chunksize=2): f.write(json.dumps(r)+'\n'); f.flush()
