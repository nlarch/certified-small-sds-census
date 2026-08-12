#!/usr/bin/env python3
"""Proof-producing subcase for SDS(36,11,2,[2,18])."""
import argparse,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from pysat.card import CardEnc,EncType
from pysat.solvers import Solver
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.sat_encoding import encode  # noqa:E402
INSTANCE=parse_name('SDS(36,11,2,[2,18])');PATTERNS=((0,3,3,3),(3,3,0,3),(3,0,3,3),(3,3,3,0));CHECKER=ROOT/'tools'/'drat-trim-src'/'drat-trim'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--pattern-index',type=int,choices=range(4),required=True);a=p.parse_args();pattern=PATTERNS[a.pattern_index]
 cells=[[],[],[],[]]
 for g in range(36):x,y=divmod(g,18);cells[2*x+y%2].append(g)
 e=encode(INSTANCE,'totalizer');top=e.cnf.nv
 for cell,s in zip(cells,pattern):
  lits=[e.positive_variables[g] for g in cell]+[-e.negative_variables[g] for g in cell]
  c=CardEnc.equals(lits,s+9,top_id=top,encoding=EncType.totalizer);top=c.nv;e.cnf.extend(c.clauses)
 d=ROOT/'artifacts'/'sat'/'v36_11_2_c2x18_subcases';d.mkdir(parents=True,exist_ok=True);stem=d/f'pattern_{a.pattern_index}';formula=stem.with_suffix('.cnf');proof=stem.with_suffix('.drat');check=stem.with_suffix('.check.txt');report=stem.with_suffix('.json')
 e.cnf.to_file(str(formula),comments=[f'c instance {INSTANCE.name}',f'c complete C2^2 cell pattern {pattern}','c exact totalizer autocorrelation encoding'])
 t=time.perf_counter()
 with Solver(name='glucose4',bootstrap_with=e.cnf.clauses,with_proof=True) as s:
  ans=s.solve();stats=s.accum_stats();trace=None if ans else s.get_proof()
 seconds=time.perf_counter()-t
 if ans:raise SystemExit('unexpected SAT')
 proof.write_text('\n'.join(trace)+'\n');r=subprocess.run([str(CHECKER),str(formula),str(proof),'-f'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);check.write_text(r.stdout);verified=r.returncode==0 and 's VERIFIED' in r.stdout
 if not verified:raise SystemExit('checker failed')
 doc={'schema':'v36-11-2-c2x18-subcase-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'instance':INSTANCE.name,'pattern_index':a.pattern_index,'pattern':pattern,'all_patterns':PATTERNS,'result':'UNSAT','solve_seconds':seconds,'solver_stats':stats,'formula':{'path':str(formula.relative_to(ROOT)),'sha256':sha(formula),'variables':e.cnf.nv,'clauses':len(e.cnf.clauses)},'proof':{'path':str(proof.relative_to(ROOT)),'sha256':sha(proof),'bytes':proof.stat().st_size},'checker':{'verified':verified,'source_commit':subprocess.check_output(['git','-C',str(CHECKER.parent),'rev-parse','HEAD'],text=True).strip(),'binary_sha256':sha(CHECKER),'output_path':str(check.relative_to(ROOT)),'output_sha256':sha(check)}}
 report.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n');print(json.dumps({'pattern':pattern,'seconds':seconds,'proof_bytes':proof.stat().st_size,'verified':verified},indent=2))
if __name__=='__main__':main()

