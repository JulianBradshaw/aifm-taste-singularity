import sys, os, json
import mc
B={}
for l in open('mc300.jsonl'):
    r=json.loads(l)
    if r['sc']=='c_w0.5_fix15' and r.get('beta'): B[r['i']]=1.0/r['beta']
mc.SC.update({'d_fixb_50x':(mc.me(.5)/mc.BASE,50.0),'e_fixb_unb':(mc.me(.5)/mc.BASE,1e5),'a_fixb_unb':(1.0,1e5)})
_job=mc.job
def job(a):
    i,sc=a
    if i not in B: return dict(i=i,sc=sc,err='nobase')
    os.environ['AIFM_FIX_R']=repr(B[i]); return _job(a)
if __name__=='__main__':
    from multiprocessing import get_context
    jobs=[(i,sc) for i in range(mc.N) for sc in ['d_fixb_50x','e_fixb_unb','a_fixb_unb']]
    with get_context('fork').Pool(4, maxtasksperchild=50) as pool, open(mc.OUT,'w') as f:
        for r in pool.imap_unordered(job,jobs,chunksize=2): f.write(json.dumps(r)+'\n'); f.flush()
