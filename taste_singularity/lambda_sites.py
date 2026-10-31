import os, sys, io, json, contextlib, logging
ROOT = os.path.abspath(os.environ.get('AIFM_ROOT', '..'))
sys.path.insert(0, ROOT)
logging.disable(logging.CRITICAL)
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    from progress_model import ProgressModel, lamsite
    from progress_model.parameters import Parameters
    from progress_model.time_series import generate_time_series_from_dict
    from api.index import drop_unknown_params
import base_run as run
preset = run.preset
TS = ['constant_training_system_performance_growth_rate','slowdown_year','post_slowdown_training_system_performance_growth_rate']

def _once(p):
    with contextlib.redirect_stdout(io.StringIO()):
        params = Parameters(**drop_unknown_params({k: v for k, v in p.items() if k not in TS}))
        ts = generate_time_series_from_dict({k: p[k] for k in TS}, os.path.join(ROOT, 'inputs/input_data.csv'))
        m = ProgressModel(params, ts); m.compute_progress_trajectory([2017, 2200], 0.0)
    return m, ts

def model_run(p, sites=None, detail=False):
    pdy = float(p['present_day'])
    os.environ['LAM_SITES'] = json.dumps(sites or {}); os.environ['LAM_PD'] = repr(pdy)
    os.environ.pop('LAM_XREF', None)
    ts = generate_time_series_from_dict({k: p[k] for k in TS}, os.path.join(ROOT, 'inputs/input_data.csv'))
    os.environ['LAM_H0'] = repr(float(np.exp(np.interp(pdy, ts.time, ts.log_L_HUMAN))))
    xref = None
    if sites and 'dynamics' in sites:
        m1, ts1 = _once(p); t1 = np.asarray(m1.results['times'])
        C0 = float(np.exp(np.interp(pdy, ts1.time, ts1.log_inference_H100e)))
        pr = float(np.interp(pdy, t1, np.asarray(m1.results['progress'], float)))
        xref = float(m1.params.automation_model.coding_labor_optimal_ces(float(os.environ['LAM_H0']), C0, np.log(10)*pr, m1.params))
        os.environ['LAM_XREF'] = repr(xref)
    m, _ = _once(p)
    R = m.results; ms = R['milestones']; t = np.asarray(R['times'])
    at = lambda k, tt: float(np.interp(tt, t, np.asarray(R[k], float)))
    ac = ms['AC']['time']; asi = ms.get('ASI', {}).get('time')
    out = dict(ac=ac, asi=asi, f_now=at('automation_fraction', pdy), prog_now=at('progress', pdy),
               prog_ac=float(m.params.progress_at_aa), r_sw=float(m.params.r_software), xref=xref,
               serial_now=at('serial_coding_labor_multipliers', pdy))
    if detail: out['model'] = m
    return out
