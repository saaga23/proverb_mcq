import json

with open(r'c:\Users\USER\Downloads\THe proverbeval container\MCQ\proverbgap-mcq.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

meta = nb.get('metadata', {})
ks = meta.get('kernelspec', {})
print(f"Kernel: {ks.get('display_name', 'unknown')}")
print(f"Total cells: {len(nb['cells'])}")
print()

for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    print(f"=== Cell {i} ({cell['cell_type']}) [{len(src)} chars] ===")
    print(src)
    print()
