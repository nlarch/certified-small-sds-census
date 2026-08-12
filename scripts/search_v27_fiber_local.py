#!/usr/bin/env python3
"""Character-fiber-preserving annealing for the six hard order-27 entries."""
import hashlib,itertools,json,math,random,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.validator_reference import validate as vr  # noqa:E402
from sds.validator_independent import validate as vi  # noqa:E402
from scripts.search_unresolved_local import tables,correlations,objective,proposed_correlations  # noqa:E402
CASES=(('SDS(27,17,4,[3,3,3])',(2,3,6)),('SDS(27,17,4,[3,9])',(2,3,6)),('SDS(27,22,3,[3,3,3])',(1,3,6)),('SDS(27,22,3,[3,9])',(1,3,6)),('SDS(27,22,9,[3,3,3])',(3,6,7)),('SDS(27,22,9,[3,9])',(3,6,7)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allocations(instance,pattern):
 out=[]
 for supports in itertools.product(range(10),repeat=3):
  if sum(supports)!=instance.k:continue
  pn=[]
  for support,s in zip(supports,pattern):
   if support<abs(s) or (support+s)%2:break
   pn.append(((support+s)//2,(support-s)//2,9-support))
  else:out.append(tuple(pn))
 return out
def search(name,pattern,index,restarts=96,steps=5000):
 inst=parse_name(name);minus,plus=tables(inst);allocs=allocations(inst,pattern);assert allocs;cells=[list(range(9*i,9*i+9)) for i in range(3)];runs=[];witness=None;t0=time.perf_counter()
 for restart in range(restarts):
  seed=2700000+index*10000+restart;rng=random.Random(seed);allocation=allocs[restart%len(allocs)];vector=[]
  for p,n,z in allocation:
   part=[1]*p+[-1]*n+[0]*z;rng.shuffle(part);vector.extend(part)
  corr=correlations(vector,minus);current=objective(inst,corr);best=current;bestv=tuple(vector);accepted=0
  for step in range(steps):
   cell=cells[rng.randrange(3)];p,q=rng.sample(cell,2)
   if vector[p]==vector[q]:continue
   candidate_corr=proposed_correlations(vector,corr,p,q,minus,plus);candidate=objective(inst,candidate_corr);fraction=step/max(1,steps-1);temp=10*(.01/10)**fraction;delta=candidate-current
   if delta<=0 or rng.random()<math.exp(-delta/temp):
    vector[p],vector[q]=vector[q],vector[p];corr=candidate_corr;current=candidate;accepted+=1
    if current<best:
     best=current;bestv=tuple(vector)
     if best==0:break
  runs.append({'seed':seed,'allocation':allocation,'best_objective':best,'best_vector':bestv,'accepted_moves':accepted})
  if best==0:witness=bestv;break
 validation=None
 if witness:
  validation={'coefficient_vector':witness,'reference':vr(inst,witness),'independent':vi(inst,witness)};assert validation['reference']['valid'] and validation['independent']['valid']
 best=min(runs,key=lambda r:r['best_objective'])
 return {'instance':name,'result':'EXISTS' if witness else 'NO_CONSTRUCTION_FOUND','fiber_pattern':pattern,'pattern_completeness':'All six permutations are equivalent under translations (3-cycles) and inversion (transposition).','feasible_cell_compositions':allocs,'restarts_completed':len(runs),'steps_per_restart':steps,'seed_offset':2700000+index*10000,'best_objective':best['best_objective'],'best_vector':best['best_vector'],'runs':runs,'validation':validation,'runtime_seconds':time.perf_counter()-t0,'evidence_warning':None if witness else 'Heuristic failure is not nonexistence evidence.'}
def main():
 report={'schema':'v27-fiber-preserving-local-search-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'instances':[search(n,p,i) for i,(n,p) in enumerate(CASES)]};out=ROOT/'artifacts'/'runs'/'v27_fiber_local_search.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(out.relative_to(ROOT)),'sha256':sha(out),'results':[(x['instance'],x['result'],x['best_objective'],x['restarts_completed']) for x in report['instances']]},indent=2))
if __name__=='__main__':main()
