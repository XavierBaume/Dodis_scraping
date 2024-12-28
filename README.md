Scripts utilisés pour :
(1) Extraire les données des pages du site Dodis vers un fichier JSON
(2) Convertir le fichier JSON vers un fichier CSV
(3) Effectuer un post-traitement du fichier CSV pour la BD.

Les fichiers JSON et CSV succesifs sont joints.

Le fichier dodis_dataBaseRendu_postcorrected.csv constitue l'élément final transmis dans le 1er rendu. 

(4) Le fichier précédent a été réarrangé selon l'ordre des colonnes, en particulier celles relatives à 'location'. Ces ajouts ont directement été intégrés dans le script Post_correction_csv_rendu.py. Dans un second temps, deux scripts Python (dd.mm.yyyy_to_dd-mm-yyyy.py puis DD-MM-YYYY_to_YYYY-MM-DD.py) ont été exécutés afin de normaliser la syntaxe des dates. Le fichier final utilisé pour l'import est donc bis_dodis_dataBaseRendu_postcorrected.csv.
