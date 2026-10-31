import json, numpy as np, collections
R=[json.loads(l) for l in open('mc2_300.jsonl')]+[dict(json.loads(l),lam=0.65) for l in open('mc300.jsonl')]
def key(r):
    s=r['sc']
    if s.startswith('ref_w'): return (0.65,15,float(s[5:]))
    if s=='c_w0.5_fix15': return (0.65,15,0.5)
    if s.startswith('cell_'):
        _,l,a,w=s.split('_'); return (float(l),int(a),float(w[1:]))
by=collections.defaultdict(list)
for r in R:
    k=key(r)
    if k and 'err' not in r and r.get('m') and r.get('beta'): by[k].append(r)
print('λ ceil w | n | P(TOS) | med AC→ASI | med ASI | P(ASI<2030)')
for k in sorted(by):
    L=by[k]; ac=np.array([r['ac'] or np.inf for r in L]); asi=np.array([r['asi'] or np.inf for r in L])
    tk=np.where(np.isfinite(ac),asi-ac,np.inf)
    print(k,len(L),f"{np.mean([r['m']>r['beta'] for r in L]):.2f}",f"{np.median(tk):.2f}",f"{np.median(asi):.1f}",f"{np.mean(asi<2030):.2f}")
