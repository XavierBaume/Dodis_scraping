import pandas as pd

file_path = 'bis_dodis_dataBaseRendu_transformed_final.csv'
data = pd.read_csv(file_path)

# Remplacer les points par des tirets dans la colonne 'dates_document_date'
data['dates_document_date'] = data['dates_document_date'].str.replace('.', '-', regex=False)

modified_file_path = '/mnt/data/bis_dodis_dataBaseRendu_transformed_final_modified.csv'
data.to_csv(modified_file_path, index=False)

print(f"Le fichier modifié a été sauvegardé à : {modified_file_path}")
