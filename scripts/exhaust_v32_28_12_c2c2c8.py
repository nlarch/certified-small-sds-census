#!/usr/bin/env python3
"""Exhaust all rank-three real-character survivors for C2 x C2 x C8."""
import hashlib,itertools,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.validator_independent import validate as vi  # noqa:E402
INSTANCE=parse_name('SDS(32,28,12,[2,2,8])')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def patterns():
 H=tuple(itertools.product((0,1),repeat=3));out=[]
 for signs in itertools.product((-4,4),repeat=7):
  spec=(20,)+signs;vals=[]
  for x in H:
   num=sum(v*(-1 if sum(a*b for a,b in zip(c,x))%2 else 1) for c,v in zip(H,spec))
   if num%8:break
   vals.append(num//8)
  else:
   if all(-4<=z<=4 for z in vals):out.append(tuple(vals))
 assert len(out)==64;return out
OPTIONS={s:[] for s in range(-4,5)}
for values in itertools.product((-1,0,1),repeat=4):OPTIONS[sum(values)].append((values,values.count(1),values.count(-1)))
def fillings(pattern):
 def visit(i,p,n,chosen):
  if p>24 or n>4:return
  remaining=4*(8-i)
  if p+remaining<24 or n+remaining<4:return
  if i==8:
   if p==24 and n==4:yield tuple(chosen)
   return
  for values,pp,nn in OPTIONS[pattern[i]]:yield from visit(i+1,p+pp,n+nn,chosen+[values])
 yield from visit(0,0,0,[])
def vector_from_cells(cells):
 vector=[0]*32
 # quotient cell (a,b,last parity); four positions have last coordinates parity+2j.
 for qi,values in enumerate(cells):
  a=(qi>>2)&1;b=(qi>>1)&1;parity=qi&1;base=(a*2+b)*8+parity
  for j,value in enumerate(values):vector[base+2*j]=value
 return tuple(vector)
def subtraction_table():
 coords=[]
 for raw in range(32):coords.append((raw//16,(raw//8)%2,raw%8))
 def rank(x):return (x[0]*2+x[1])*8+x[2]
 return [[rank(((coords[g][0]-coords[h][0])%2,(coords[g][1]-coords[h][1])%2,(coords[g][2]-coords[h][2])%8)) for g in range(32)] for h in range(32)]
def check(v,sub):
 for h in range(1,32):
  if sum(v[g]*v[sub[h][g]] for g in range(32))!=12:return False
 return True
def main():
 t=time.perf_counter();pats=patterns();sub=subtraction_table();count=0;feasible=0;solutions=[]
 for pat in pats:
  local=0
  for cells in fillings(pat):
   v=vector_from_cells(cells);count+=1;local+=1
   if check(v,sub):assert vi(INSTANCE,v)['valid'];solutions.append(v)
  if local:feasible+=1
 assert feasible==56 and count==2207744
 doc={'schema':'v32-28-12-c2c2c8-walsh-exhaustion-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'instance':INSTANCE.name,'result':'EXISTS' if solutions else 'NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION','mathematical_argument':['The full real-character quotient is C2^3 with eight size-four cells.','All 2^7 nonprincipal +/-4 spectra are inverse-Walsh transformed; exactly 64 yield bounded integral cell sums.','Every four-coefficient preimage of each cell sum is explicitly generated, with exact composition 24 positive, 4 negative, 4 zero.','Exactly 56 patterns admit 2207744 full vectors; every vector is checked against all full autocorrelations.'],'spectra_tested':128,'bounded_integral_patterns':64,'patterns_with_exact_composition':feasible,'full_vectors_tested':count,'solutions':solutions,'runtime_seconds':time.perf_counter()-t,'environment':{'python':platform.python_version(),'platform':platform.platform()}};out=ROOT/'artifacts'/'runs'/'v32_28_12_c2c2c8_walsh_exhaustion.json';out.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(out.relative_to(ROOT)),'sha256':sha(out),'result':doc['result'],'vectors':count,'solutions':len(solutions),'runtime':doc['runtime_seconds']},indent=2))
if __name__=='__main__':main()
