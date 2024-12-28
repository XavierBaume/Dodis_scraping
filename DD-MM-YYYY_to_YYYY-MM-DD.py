import pandas as pd

# Charger le fichier CSV
file_path = 'path_to_your_file.csv'  # Remplacez par le chemin de votre fichier
data = pd.read_csv(file_path)

# Convertir les dates dans la colonne 'dates_document_date' du format DD-MM-YYYY à YYYY-MM-DD
data['dates_document_date'] = pd.to_datetime(data['dates_document_date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

# Sauvegarder le fichier modifié
output_path = 'modified_file.csv'  # Remplacez par le chemin de sortie souhaité
data.to_csv(output_path, index=False)

print(f"Fichier modifié sauvegardé à : {output_path}")
