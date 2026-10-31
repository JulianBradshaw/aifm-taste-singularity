import sys, os, json, signal, time
sys.path.insert(0,os.path.join(os.environ['AIFM_ROOT'],'scripts/pipelines')); sys.path.insert(0,os.environ['AIFM_ROOT'])
import logging; logging.disable(logging.CRITICAL)
import numpy as np
from numpy.random import SeedSequence
import batch_rollout as br
from progress_model.parameters import Parameters
from progress_model import ProgressModel
from progress_model.time_series import generate_time_series_from_dict, load_time_series_data
from multiprocessing import get_context
CFG=os.environ['AIFM_ROOT']+'/config/sampling_config_q2_eli.yaml'
user=br._load_config(CFG); pd=user['parameters']; tsd=user.get('time_series_parameters',{}); cm=user.get('correlation_matrix')
SEED=int(user.get('seed',20260810)); N=int(sys.argv[1]); OUT=sys.argv[2]
INP=str((br.REPO_ROOT/user.get('input_data','inputs/input_data.csv')).resolve()) if not os.path.isabs(user.get('input_data','inputs/input_data.csv')) else user['input_data']
ss=SeedSequence(SEED)
if cm is not None:
    lat=br._calibrate_gaussian_copula_latent_corr(pd, cm['parameters'], np.array(cm['correlation_matrix'],float), np.random.default_rng(ss.spawn(1)[0]),
        interpretation=str(cm.get('correlation_type','spearman')), calibration_samples=int(cm.get('calibration_samples',20000)))
    cm['latent_correlation_matrix']=lat.tolist()
allp=dict(pd); allp.update(tsd); seeds=ss.spawn(N)
LAM=0.65
BASE=0.2409892194931128; MS=0.615; MD=0.24
me=lambda w: w*MD+(1-w)*MS
SC={'a_default':(1.0,None),'b_tasteval':(MS/BASE,None),'c_w0.3':(me(.3)/BASE,None),'c_w0.5':(me(.5)/BASE,None),'c_w0.7':(me(.7)/BASE,None),
    'c_w0.5_fix15':(me(.5)/BASE,15.142135623730951),'d_w0.5_50x':(me(.5)/BASE,50.0),'e_w0.5_unb':(me(.5)/BASE,1e5),
    'a_fix15':(1.0,15.142135623730951)}
def _alarm(s,f): raise TimeoutError()
def job(a):
    i,sc=a; k,asym=SC[sc]
    signal.signal(signal.SIGALRM,_alarm); signal.alarm(60)
    try:
        with br._suppress_noise():
            s=br._sample_parameter_dict(allp, np.random.default_rng(seeds[i]), cm)
            P={x:v for x,v in s.items() if x in pd}; T={x:v for x,v in s.items() if x in tsd}
            P.setdefault('horizon_extrapolation_type', br.cfg.DEFAULT_HORIZON_EXTRAPOLATION_TYPE); P.setdefault('taste_schedule_type', br.cfg.DEFAULT_TASTE_SCHEDULE_TYPE)
            P['parallel_penalty']=LAM; P['ai_research_taste_slope']=float(P['ai_research_taste_slope'])*k
            if asym is not None: P['inf_labor_asymptote']=asym
            data=load_time_series_data(INP); rd=generate_time_series_from_dict(T, INP, data) if T else data
            m=ProgressModel(Parameters(**P), rd); m.compute_progress_trajectory([2017.0,2200.0],0.0)
            R=m.results; ms=R.get('milestones',{})
            g=lambda n: (ms.get(n) or {}).get('time')
            out=dict(i=i,sc=sc,m=R.get('slope_times_log_f'),beta=R.get('beta_software'),ac=g('AC'),asi=g('ASI'),sar=g('SAR'),
                     slope=P['ai_research_taste_slope'],asym=P['inf_labor_asymptote'])
    except Exception as e:
        out=dict(i=i,sc=sc,err=type(e).__name__)
    signal.alarm(0)
    out={k2:(float(v) if isinstance(v,(np.floating,)) else v) for k2,v in out.items()}
    return out
if __name__=='__main__':
    scs=sys.argv[3].split(',') if len(sys.argv)>3 else list(SC)
    jobs=[(i,sc) for i in range(N) for sc in scs]
    t=time.time()
    with get_context('fork').Pool(4, maxtasksperchild=50) as pool, open(OUT,'w') as f:
        for n,r in enumerate(pool.imap_unordered(job,jobs,chunksize=2)):
            f.write(json.dumps(r)+'\n'); f.flush()
    print('done',time.time()-t)
