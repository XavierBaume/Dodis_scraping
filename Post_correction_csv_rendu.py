#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import re

# Charger le fichier CSV
input_file = "dodis_dataBaseRendu_transformed_corrected.csv"
output_file = "dodis_dataBaseRendu_transformed_final.csv"

# Charger le fichier en DataFrame
df = pd.read_csv(input_file)

# Supprimer les colonnes inutiles
columns_to_remove = [
    "document_if_published_volume_link",
    "document_if_published_volume_reference",
    "document_reference",
    "document_publication_date",
    "document_related_to_dodis_docs_item1",
    "document_related_to_dodis_docs_item2",
    "document_related_to_dodis_docs_item3",
    "document_related_to_dodis_docs_item4",
    "document_related_to_dodis_docs_item5",
    "document_related_to_dodis_docs_item6"
]
df = df.drop(columns=columns_to_remove, errors='ignore')

# Supprimer la seconde occurrence de 'document_summary' si elle existe
summary_columns = [col for col in df.columns if col == 'document_summary']
if len(summary_columns) > 1:
    df = df.drop(columns=summary_columns[1], errors='ignore')

# Diviser la colonne 'locations_archives_recipient_location' en plusieurs colonnes
if 'locations_archives_recipient_location' in df.columns:
    location_cols = df['locations_archives_recipient_location'].str.split(';', expand=True)
    location_cols.columns = [f"location_{i+1}" for i in range(location_cols.shape[1])]
    df = pd.concat([df, location_cols], axis=1)
    df = df.drop(columns=['locations_archives_recipient_location'], errors='ignore')

# Filtrer les valeurs dans 'document_if_published_publication_details'
if 'document_if_published_publication_details' in df.columns:
    df['document_if_published_publication_details'] = df['document_if_published_publication_details'].apply(
        lambda x: re.search(r"(Bd\.\s?\d{2})", x).group(0) if isinstance(x, str) and re.search(r"(Bd\.\s?\d{2})", x) else ""
    )

# Réorganiser les colonnes selon les instructions
columns_order = [
    'document_digital_id',  # Interverti avec dates_document_date
    'dates_document_date',
    'document_summary',  # Placé en 3ᵉ position
    'document_type_document',  # Placé en 4ᵉ position
    'location_1',  # Première colonne des locations
    'location_2',  # Placé en 5ᵉ position (première valeur après split)
] + [col for col in df.columns if col not in [
    'document_digital_id', 'dates_document_date', 'document_summary', 
    'document_type_document', 'location_1', 'location_2'
]]

# Réordonner les colonnes
df = df[columns_order]

# Sauvegarder le fichier modifié
df.to_csv(output_file, index=False)

print(f"Fichier transformé et enregistré sous {output_file}")


# In[ ]:




