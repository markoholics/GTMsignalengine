"""Copy outputs/ into web/outputs/ (plus a projects.json index) so web/ is a self-contained static site."""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src, dst = ROOT / "outputs", ROOT / "web" / "outputs"
if dst.exists():
    shutil.rmtree(dst)
dst.mkdir(parents=True)
slugs = sorted(p.name for p in src.iterdir() if (p / "project.json").exists())
for s in slugs:
    shutil.copytree(src / s, dst / s)
(dst / "projects.json").write_text(json.dumps(slugs))
print("built", slugs)
