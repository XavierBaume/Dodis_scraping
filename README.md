Scripts utilisés pour :
(1) Extraire les données des pages du site Dodis vers un fichier JSON
(2) Convertir le fichier JSON vers un fichier CSV
(3) Effectuer un post-traitement du fichier CSV pour la BD.

Les fichiers JSON et CSV succesifs sont joints.

Le fichier dodis_dataBaseRendu_postcorrected.csv constitue l'élément final transmis dans le 1er rendu. Le fichier bis_dodis_dataBaseRendu_postcorrected.csv est réarrangé selon l'ordre des colonnes

À partir du dump de notre base de données, dans lequel les contenus du fichier bis_dodis_dataBaseRendu_postcorrected.csv ont été intégrés, un script Python (dd.mm.yyyy_to_dd-mm-yyyy.py) a été exécuté afin de normaliser la syntaxe des dates.
