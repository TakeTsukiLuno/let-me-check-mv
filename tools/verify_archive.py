from pathlib import Path
import hashlib, sys
root=Path(__file__).resolve().parents[1]
failed=[]
for record in (root/'SHA256SUMS.txt').read_text('utf-8').splitlines():
    if not record.strip(): continue
    digest, rel=record.split('  ',1)
    actual=hashlib.sha256((root/rel).read_bytes()).hexdigest()
    if digest!=actual: failed.append(rel)
print('PASS' if not failed else 'FAIL',len(failed), 'bad files')
for x in failed: print(x)
sys.exit(bool(failed))
