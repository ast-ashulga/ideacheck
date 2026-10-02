import json,sys
sys.path.insert(0,'scripts/phase0')
import retrieve
from pathlib import Path
d=Path('phase0/runs/control-01')
spec=json.loads((d/'queries.json').read_text())
hits=json.loads((d/'remote_hits.json').read_text())
hits.update(retrieve.run_local(spec['local']))
c=retrieve.merge(hits)
(d/'candidates.json').write_text(json.dumps(c,indent=1,ensure_ascii=False))
print(len(c))
