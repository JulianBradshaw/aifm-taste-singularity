import json, sys, numpy as np, collections
rows=[json.loads(l) for l in open(sys.argv[1])]
by=collections.defaultdict(list)
for r in rows: by[r['sc']].append(r)
print('scenario n ok P(TOS) med_m/b med_AC med_ASI med_AC->ASI P(ASI<2030) P(ASI<=2200)')
import glob
for sc in ['a_default','a_fix15','b_tasteval','c_w0.3','c_w0.5','c_w0.7','c_w0.5_fix15','d_w0.5_50x','e_w0.5_unb','d_fixb_50x','e_fixb_unb','a_fixb_unb','d_fixbm_50x','e_fixbm_unb']:
    L=by.get(sc,[]); ok=[r for r in L if 'err' not in r and r.get('m') is not None and r.get('beta')]
    if not ok: continue
    tos=np.mean([r['m']>r['beta'] for r in ok]); mb=np.median([r['m']/r['beta'] for r in ok])
    ac=np.array([r['ac'] if r['ac'] else np.inf for r in ok]); asi=np.array([r['asi'] if r['asi'] else np.inf for r in ok])
    tk=np.where(np.isfinite(ac),asi-ac,np.inf)
    print(sc,len(L),len(ok),f"{tos:.2f}",f"{mb:.2f}",f"{np.median(ac):.2f}",f"{np.median(asi):.2f}",f"{np.median(tk):.2f}",f"{np.mean(asi<2030):.2f}",f"{np.mean(np.isfinite(asi)):.2f}")
