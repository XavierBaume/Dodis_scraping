#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import csv
from collections import defaultdict

# Charger les données JSON
with open('dodis_dataBaseRendu.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Fonction pour aplatir les objets JSON tout en gérant les listes
def flatten_json(json_obj, prefix=''):
    """Aplatit récursivement un objet JSON."""
    items = {}
    list_counters = defaultdict(int)  # Garde une trace des listes par clé
    for key, value in json_obj.items():
        new_key = f"{prefix}_{key}" if prefix else key
        if isinstance(value, dict):
            items.update(flatten_json(value, prefix=new_key))
        elif isinstance(value, list):
            # Traite les éléments de la liste dans l'ordre et les numérote proprement
            for i, element in enumerate(value, start=1):
                list_counters[new_key] += 1
                items[f"{new_key}_item{i}"] = element
        else:
            items[new_key] = value
    return items

# Aplatir toutes les entrées du tableau JSON
flattened_data = [flatten_json(item) for item in data]

# Extraire les en-têtes de manière ordonnée
headers = set()
for item in flattened_data:
    headers.update(item.keys())

# Trier les en-têtes par nom, tout en mettant les colonnes numérotées dans le bon ordre
def sorted_headers(header_list):
    """Trie les en-têtes et gère correctement les colonnes avec des numéros."""
    def natural_key(header):
        parts = header.rsplit('_item', 1)
        return (parts[0], int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0)
    return sorted(header_list, key=natural_key)

sorted_headers_list = sorted_headers(headers)

# Écrire dans un fichier CSV
csv_file_path = 'dodis_dataBaseRendu_transformed_corrected.csv'
with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=sorted_headers_list)
    writer.writeheader()
    writer.writerows(flattened_data)

print(f"Fichier CSV corrigé et trié enregistré à : {csv_file_path}")


# In[ ]:




