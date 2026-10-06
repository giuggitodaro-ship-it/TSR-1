"""Render all technical and functional views from an existing TSR1.blend."""
import sys,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import build_tsr1 as b
b.u.MATERIALS={m.name.removeprefix('TSR1_'):m for m in bpy.data.materials if m.name.startswith('TSR1_')}
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None
b.render_views(args)
from finalize_tsr1 import finalize
finalize()
