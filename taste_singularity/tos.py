import sys, os, json, time
os.environ.setdefault('AIFM_ROOT', '.')
import base_run as R
def go(over, preset='eli-08-16-26'):
    p = dict(R.preset(preset)); p.update(over)
    with R.contextlib.redirect_stdout(R.io.StringIO()):
        r = R.client.post('/api/compute', json={'parameters': p, 'time_range':[2017,2200], 'initial_progress':0.0})
    js = r.get_json()
    if r.status_code != 200: return {'err': str(js)[:300]}
    ms = js['milestones']; s = js.get('summary', {})
    ac = ms.get('AC',{}).get('time'); asi = ms.get('ASI',{}).get('time')
    return dict(ac=ac, asi=asi, takeoff=(asi-ac) if ac and asi else None,
                m=s.get('slope_times_log_f'), beta=s.get('beta_software'), r=s.get('r_software'),
                keys=None)
if __name__=='__main__':
    t=time.time(); out=go({'parallel_penalty':0.65}); print(out, time.time()-t)
