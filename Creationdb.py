import csv
import sqlite3
conn = sqlite3.connect('pollution.sqlite')

c = conn.cursor()


## ======== Création de la table 'stations' ================================================================

print("Création de la base de données 'stations' ...")
c.execute('''DROP TABLE IF EXISTS stations''')
c.execute('''CREATE TABLE stations       \
              ( X REAL,                         \
                Y REAL,                         \
                id TEXT,                       \
                label TEXT,                   \
                insee TEXT,               \
                label_commune TEXT,               \
                departement INT,               \
                label_departement TEXT,                      \
                type INT,                \
                typologie TEXT,                 \
                influence TEXT,                 \
                date_debut TEXT,                 \
                date_fin TEXT,                 \
                en_service INT,                 \
                OBJECTID INT PRIMARY KEY   )''')
print("... Base de données 'stations' créée. \n")


print("Chargement des données de 'Stations.csv' ...")
with open('Stations.csv', newline='') as csvfile :
    lecturefichier = csv.reader(csvfile, delimiter=';', quotechar='"')
    premiereligne = True
    for row in lecturefichier :
        if premiereligne :
            premiereligne = False
        else :
            c.execute('INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)', tuple(v for v in row))
            conn.commit()
print("... Données de 'Stations.csv' chargées. \n")



## ======== Création de la table moyennes_journalieres =====================================================================

