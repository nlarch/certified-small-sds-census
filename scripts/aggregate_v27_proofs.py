#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'artifacts'/'sat'/'v27_subcases';OUT=ROOT/'artifacts'/'runs'/'v27_certified_sat.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rs=[]
 for c in range(4):
  for p in range(6):
   r=json.loads((D/f'case_{c}_pattern_{p}.json').read_text());assert r['case_index']==c and r['pattern_index']==p and r['result']=='UNSAT' and r['checker']['verified'];assert sha(ROOT/r['formula']['path'])==r['formula']['sha256'];assert sha(ROOT/r['proof']['path'])==r['proof']['sha256'];assert sha(ROOT/r['checker']['output_path'])==r['checker']['output_sha256'];rs.append(r)
 results=[]
 for c in range(4):
  sub=[r for r in rs if r['case_index']==c];results.append({'instance':sub[0]['instance'],'result':'NONEXISTENT_BY_CHECKED_SAT_PROOFS','patterns':[r['pattern'] for r in sub],'subcases':sub})
 doc={'schema':'v27-certified-nonexistence-v1','completed_at_utc':max(r['completed_at_utc'] for r in rs),'result_count':4,'all_twenty_four_proofs_checked':True,'completeness_argument':['Each named group has an order-three character with three fibers of size nine.','The cyclotomic integer identity and principal sum leave exactly the six recorded bounded fiber-sum patterns for each parameter set.','Every pattern CNF includes the exact coefficient composition and all full autocorrelation equations; all 24 UNSAT proofs pass independent forward DRAT checking.'],'results':results};OUT.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'results':[x['instance'] for x in results]},indent=2))
if __name__=='__main__':main()
