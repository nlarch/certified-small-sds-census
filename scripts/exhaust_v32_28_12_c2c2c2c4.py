#!/usr/bin/env python3
"""Exhaust all full-rank real-character survivors for C2^3 x C4."""
import hashlib,itertools,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sds.model import parse_name  # noqa:E402
from sds.validator_reference import validate as vr  # noqa:E402
from sds.validator_independent import validate as vi  # noqa:E402
INSTANCE=parse_name('SDS(32,28,12,[2,2,2,4])')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walsh_patterns():
 H=tuple(itertools.product((0,1),repeat=4));out=[]
 for signs in itertools.product((-4,4),repeat=15):
  spec=(20,)+signs;vals=[]
  for x in H:
   numerator=sum(value*(-1 if sum(a*b for a,b in zip(character,x))%2 else 1) for character,value in zip(H,spec))
   if numerator%16:break
   vals.append(numerator//16)
  else:
   if all(-2<=value<=2 for value in vals):out.append(tuple(vals))
 assert len(out)==688;return out
def cell_options(cell_sum):
 return {2:((1,1),),1:((1,0),(0,1)),0:((0,0),(1,-1),(-1,1)),-1:((-1,0),(0,-1)),-2:((-1,-1),)}[cell_sum]
def vector_from_cells(values):
 # quotient cell order is (a,b,c,last parity); the two positions differ by +2 in C4.
 vector=[0]*32
 for qi,pair in enumerate(values):
  a=(qi>>3)&1;b=(qi>>2)&1;c=(qi>>1)&1;parity=qi&1;base=((a*2+b)*2+c)*4+parity
  vector[base],vector[base+2]=pair
 return tuple(vector)
def exact_composition_fillings(pattern):
 options=[cell_options(s) for s in pattern]
 def visit(index,positive,negative,chosen):
  if positive>24 or negative>4:return
  remaining=2*(16-index)
  if positive+remaining<24 or negative+remaining<4:return
  if index==16:
   if positive==24 and negative==4:yield tuple(chosen)
   return
  for pair in options[index]:
   yield from visit(index+1,positive+pair.count(1),negative+pair.count(-1),chosen+[pair])
 yield from visit(0,0,0,[])
def subtraction_table():
 coords=[]
 for raw in range(32):
  x=raw;row=[0,0,0,0]
  for j,m in reversed(list(enumerate(INSTANCE.group))):row[j]=x%m;x//=m
  coords.append(row)
 def rank(row):
  value=0
  for digit,m in zip(row,INSTANCE.group):value=value*m+digit
  return value
 return [[rank([(coords[g][j]-coords[h][j])%INSTANCE.group[j] for j in range(4)]) for g in range(32)] for h in range(32)]
def exact_check(vector,subtraction):
 for shift in range(1,32):
  if sum(vector[g]*vector[subtraction[shift][g]] for g in range(32))!=12:return False
 return True
def main():
 t0=time.perf_counter();patterns=walsh_patterns();patterns_with_fillings=0;vectors=0;solutions=[];subtraction=subtraction_table()
 for pattern in patterns:
  count_for_pattern=0
  for cells in exact_composition_fillings(pattern):
   vector=vector_from_cells(cells)
   vectors+=1;count_for_pattern+=1
   if exact_check(vector,subtraction):
    assert vi(INSTANCE,vector)['valid'];solutions.append(vector)
  if count_for_pattern:patterns_with_fillings+=1
 assert patterns_with_fillings==448 and vectors==107520
 report={'schema':'v32-28-12-c2c2c2c4-walsh-exhaustion-v1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'instance':INSTANCE.name,'result':'EXISTS' if solutions else 'NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION','mathematical_argument':['The real-character quotient of C2^3 x C4 is C2^4, with sixteen cells of two elements.','The principal character is +20 and all fifteen nonprincipal real characters are independently +/-4. Exhausting all 2^15 spectra and inverse Walsh transforming yields exactly 688 bounded integral cell-sum patterns.','For a two-element cell, each sum in {-2,-1,0,1,2} has the explicitly enumerated coefficient-pair preimages. Exact global composition is 24 positive, 4 negative, and 4 zero coefficients.','Exactly 448 Walsh patterns admit that composition, with 107520 full coefficient vectors in total. Every one is checked against the full unsymmetrized autocorrelation equation.'],'spectra_tested':2**15,'bounded_integral_patterns':len(patterns),'patterns_with_exact_composition':patterns_with_fillings,'full_vectors_tested':vectors,'solutions':solutions,'runtime_seconds':time.perf_counter()-t0,'environment':{'python':platform.python_version(),'platform':platform.platform()}}
 out=ROOT/'artifacts'/'runs'/'v32_28_12_c2c2c2c4_walsh_exhaustion.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(out.relative_to(ROOT)),'sha256':sha(out),'result':report['result'],'vectors':vectors,'solutions':len(solutions),'runtime':report['runtime_seconds']},indent=2))
if __name__=='__main__':main()
