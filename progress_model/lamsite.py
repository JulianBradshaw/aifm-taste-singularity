import os, json
_cache = [None, {}]
def lam(site, base):
    s = os.environ.get('LAM_SITES', '')
    if s != _cache[0]:
        _cache[0] = s; _cache[1] = json.loads(s) if s else {}
    return _cache[1].get(site, base)

import numpy as _np
def serial(X, t, base, cn, human):
    """Parallel labor X -> serial labor. With no history/dynamics override this is the
    model's own X**base * cn. With an override, levels are pinned at today's values and
    only the elasticity changes: lambda_history before present day, lambda_dynamics after."""
    lam('', 0)
    ov = _cache[1]
    if 'history' not in ov and 'dynamics' not in ov:
        return _np.power(X, base) * cn
    H0 = float(os.environ['LAM_H0']); PD = float(os.environ['LAM_PD'])
    lh = ov.get('history', base); ld = ov.get('dynamics', base)
    xr = H0 if human else float(os.environ.get('LAM_XREF', H0))
    Xa = _np.asarray(X, float); ta = _np.asarray(t, float)
    past = H0**base * (Xa/H0)**lh
    fut = H0**base * (xr/H0)**lh * (Xa/xr)**ld
    out = _np.where(ta < PD, past, fut) * cn
    return float(out) if out.ndim == 0 else out

_rec = []
_serial_inner = serial
def serial(X, t, base, cn, human):
    if not human and os.environ.get('LAM_RECORD') and _np.ndim(t) == 0 and abs(float(t) - float(os.environ['LAM_PD'])) < 0.01:
        _rec.append((float(t), float(X)))
    return _serial_inner(X, t, base, cn, human)
