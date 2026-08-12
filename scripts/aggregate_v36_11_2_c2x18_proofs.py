#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'artifacts'/'sat'/'v36_11_2_c2x18_subcases';OUT=ROOT/'artifacts'/'runs'/'v36_11_2_c2x18_certified_sat.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rs=[]
 for i in range(4):
  r=json.loads((D/f'pattern_{i}.json').read_text());assert r['pattern_index']==i and r['result']=='UNSAT' and r['checker']['verified'];assert sha(ROOT/r['formula']['path'])==r['formula']['sha256'];assert sha(ROOT/r['proof']['path'])==r['proof']['sha256'];assert sha(ROOT/r['checker']['output_path'])==r['checker']['output_sha256'];rs.append(r)
 doc={'schema':'v36-11-2-c2x18-certified-v1','completed_at_utc':max(r['completed_at_utc'] for r in rs),'instance':rs[0]['instance'],'result':'NONEXISTENT_BY_CHECKED_SAT_PROOFS','all_four_proofs_checked':True,'completeness_argument':['The real-character quotient of C2 x C18 is C2^2 with four size-nine cells.','Principal sum +9 and three nonprincipal values independently +/-3 inverse-Walsh transform to exactly four bounded integral patterns.','The four exact full-autocorrelation CNFs cover those patterns; every UNSAT proof passes independent forward DRAT checking.'],'subcases':rs}
 OUT.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'result':doc['result']},indent=2))
if __name__=='__main__':main()
