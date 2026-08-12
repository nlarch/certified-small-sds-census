#!/usr/bin/env python3
"""Exact SAT witness search split by one real character."""

import argparse, hashlib, json, math, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.sat_encoding import encode,decode  # noqa:E402
from sds.validator_reference import validate as vr  # noqa:E402
from sds.validator_independent import validate as vi  # noqa:E402

def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--conflicts',type=int,default=200000);p.add_argument('--tag',required=True);p.add_argument('--solver',default='glucose4');a=p.parse_args()
    instance=parse_name(a.name)
    even_index=next(i for i,m in enumerate(instance.group) if m%2==0)
    principal=math.isqrt(instance.k+instance.lam*(instance.v-1)); nonprincipal=math.isqrt(instance.k-instance.lam)
    assert principal*principal==instance.k+instance.lam*(instance.v-1) and nonprincipal*nonprincipal==instance.k-instance.lam
    patterns=((principal-nonprincipal)//2,(principal+nonprincipal)//2),((principal+nonprincipal)//2,(principal-nonprincipal)//2)
    cells=[[],[]]
    for raw in range(instance.v):
        x=raw;digits=[0]*len(instance.group)
        for j in range(len(instance.group)-1,-1,-1): digits[j]=x%instance.group[j];x//=instance.group[j]
        cells[digits[even_index]%2].append(raw)
    attempts=[]; witness=None
    for pattern_index,pattern in enumerate(patterns):
        encoded=encode(instance,'totalizer');top=encoded.cnf.nv
        for cell,required_sum in zip(cells,pattern):
            literals=[encoded.positive_variables[g] for g in cell]+[-encoded.negative_variables[g] for g in cell]
            constraint=CardEnc.equals(literals,required_sum+len(cell),top_id=top,encoding=EncType.totalizer);top=constraint.nv;encoded.cnf.extend(constraint.clauses)
        started=time.perf_counter()
        with Solver(name=a.solver,bootstrap_with=encoded.cnf.clauses) as solver:
            solver.conf_budget(a.conflicts); answer=solver.solve_limited()
            try: stats=solver.accum_stats()
            except NotImplementedError: stats={'unavailable_for_solver':a.solver}
            model=solver.get_model() if answer else None
        attempt={'pattern_index':pattern_index,'pattern':pattern,'answer':'SAT' if answer is True else 'UNSAT' if answer is False else 'UNKNOWN','solve_seconds':time.perf_counter()-started,'solver_stats':stats,'conflict_budget':a.conflicts}
        attempts.append(attempt)
        if model:
            vector=decode(encoded,model);reference=vr(instance,vector);independent=vi(instance,vector);assert reference['valid'] and independent['valid']
            witness={'coefficient_vector':vector,'reference':reference,'independent':independent};break
    result='EXISTS' if witness else 'NO_DECISION'
    item={'instance':instance.name,'result':result,'composition_positive_negative_zero':((instance.k+principal)//2,(instance.k-principal)//2,instance.v-instance.k),'restarts_completed':len(attempts),'steps_per_restart':0,'seed_offset':None,'best_objective':0 if witness else None,'best_vector':None if witness is None else witness['coefficient_vector'],'runs':attempts,'validation':witness,'runtime_seconds':sum(x['solve_seconds'] for x in attempts),'evidence_warning':None if witness else 'UNKNOWN or raw UNSAT attempts do not resolve the entry.'}
    report={'schema':'rank1-walsh-sat-search-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'command':f'.venv/bin/python scripts/search_rank1_walsh_sat.py --name {a.name} --conflicts {a.conflicts} --tag {a.tag} --solver {a.solver}','solver':a.solver,'instances':[item],'environment':{'python':platform.python_version(),'platform':platform.platform()}}
    output=ROOT/'artifacts'/'runs'/f'rank1_sat_{a.tag}.json';output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(output.relative_to(ROOT)),'sha256':sha256(output),'instance':instance.name,'result':result,'attempts':attempts,'vector':None if witness is None else witness['coefficient_vector']},indent=2))

if __name__=='__main__':main()
