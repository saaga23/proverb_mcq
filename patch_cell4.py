import json

with open("C:\\Users\\User\\Downloads\\THe proverbeval container\\MCQ\\proverbgap-pilot-v2.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and cell['source'] and '# Cell 4: Load Pilot Data' in cell['source'][0]:
        new_source = []
        for line in cell['source']:
            if "LANGUAGES =" in line:
                new_source.append("LANGUAGES = ['English', 'French', 'Arabic']\n")
            else:
                new_source.append(line)
        cell['source'] = new_source

with open("C:\\Users\\User\\Downloads\\THe proverbeval container\\MCQ\\proverbgap-pilot-v2.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
    
print("Notebook patched for 3 languages.")
