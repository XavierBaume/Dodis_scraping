import pandas as pd

file_path = 'bis_dodis_dataBaseRendu_transformed_final_modified.csv'
data = pd.read_csv(file_path)

# Convertir les dates dans la colonne 'dates_document_date' du format DD-MM-YYYY à YYYY-MM-DD
data['dates_document_date'] = pd.to_datetime(data['dates_document_date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

output_path = 'bis_dodis_dataBaseRendu_transformed_final.csv'
data.to_csv(output_path, index=False)

print(f"Fichier modifié sauvegardé à : {output_path}")
