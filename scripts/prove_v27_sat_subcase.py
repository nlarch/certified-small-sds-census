#!/usr/bin/env python3
"""Proof-producing order-three fiber subcases for selected order-27 targets."""
import argparse,hashlib,itertools,json,math,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from pysat.card import CardEnc,EncType
from pysat.solvers import Solver
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.sat_encoding import encode  # noqa:E402
NAMES=('SDS(27,17,8,[27])','SDS(27,25,16,[27])','SDS(27,25,16,[3,3,3])','SDS(27,25,16,[3,9])');CHECKER=ROOT/'tools'/'drat-trim-src'/'drat-trim'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def patterns(inst):
 S=math.isqrt(inst.k+inst.lam*26);n=inst.k-inst.lam;t=(S*S-n)//3;c0=n+t;out=[]
 for s in itertools.product(range(-9,10),repeat=3):
  if sum(s)==S and sum(x*x for x in s)==c0 and all(sum(s[j]*s[(j-h)%3] for j in range(3))==t for h in (1,2)):out.append(s)
 assert len(out)==6;return tuple(out)
def cells(inst):
 out=[[],[],[]]
 if len(inst.group)==1:
  for g in range(27):out[g%3].append(g)
 else:
  for g in range(27):out[g//(27//inst.group[0])].append(g)
 assert all(len(x)==9 for x in out);return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--case-index',type=int,choices=range(4),required=True);p.add_argument('--pattern-index',type=int,choices=range(6),required=True);a=p.parse_args();inst=parse_name(NAMES[a.case_index]);pat=patterns(inst)[a.pattern_index];e=encode(inst,'totalizer');top=e.cnf.nv
 for cell,s in zip(cells(inst),pat):
  lits=[e.positive_variables[g] for g in cell]+[-e.negative_variables[g] for g in cell];c=CardEnc.equals(lits,s+9,top_id=top,encoding=EncType.totalizer);top=c.nv;e.cnf.extend(c.clauses)
 d=ROOT/'artifacts'/'sat'/'v27_subcases';d.mkdir(parents=True,exist_ok=True);stem=d/f'case_{a.case_index}_pattern_{a.pattern_index}';formula=stem.with_suffix('.cnf');proof=stem.with_suffix('.drat');check=stem.with_suffix('.check.txt');report=stem.with_suffix('.json')
 e.cnf.to_file(str(formula),comments=[f'c instance {inst.name}',f'c complete order-three fiber pattern {pat}','c exact totalizer full-autocorrelation encoding'])
 t=time.perf_counter()
 with Solver(name='glucose4',bootstrap_with=e.cnf.clauses,with_proof=True) as s:ans=s.solve();stats=s.accum_stats();trace=None if ans else s.get_proof()
 sec=time.perf_counter()-t
 if ans:raise SystemExit('unexpected SAT')
 proof.write_text('\n'.join(trace)+'\n');r=subprocess.run([str(CHECKER),str(formula),str(proof),'-f'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);check.write_text(r.stdout);verified=r.returncode==0 and 's VERIFIED' in r.stdout
 if not verified:raise SystemExit('checker failed')
 doc={'schema':'v27-certified-sat-subcase-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'instance':inst.name,'case_index':a.case_index,'pattern_index':a.pattern_index,'pattern':pat,'all_patterns':patterns(inst),'result':'UNSAT','solve_seconds':sec,'solver_stats':stats,'formula':{'path':str(formula.relative_to(ROOT)),'sha256':sha(formula),'variables':e.cnf.nv,'clauses':len(e.cnf.clauses)},'proof':{'path':str(proof.relative_to(ROOT)),'sha256':sha(proof),'bytes':proof.stat().st_size},'checker':{'verified':verified,'source_commit':subprocess.check_output(['git','-C',str(CHECKER.parent),'rev-parse','HEAD'],text=True).strip(),'binary_sha256':sha(CHECKER),'output_path':str(check.relative_to(ROOT)),'output_sha256':sha(check)}};report.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n');print(json.dumps({'instance':inst.name,'pattern':pat,'seconds':sec,'bytes':proof.stat().st_size,'verified':verified}))
if __name__=='__main__':main()

