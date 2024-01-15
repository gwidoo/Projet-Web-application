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
                id TEXT PRIMARY KEY ,                       \
                label TEXT,                   \
                insee TEXT,               \
                label_commune TEXT,               \
                departement INT,               \
                label_departement TEXT,                      \
                type INT,                \
                label_type TEXT,                \
                typologie TEXT,                 \
                influence TEXT,                 \
                date_debut TEXT,                 \
                date_fin TEXT,                 \
                en_service INT,                 \
                OBJECTID INT   )''')
print("... Base de données 'stations' créée. \n")


print("Chargement des données de 'Stations.csv' ...")
with open('Stations.csv', newline='') as csvfile :
    lecturefichier = csv.reader(csvfile, delimiter=',', quotechar='"')
    premiereligne = True
    for row in lecturefichier :
        if premiereligne :
            premiereligne = False
        else :
            c.execute('INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(v for v in row))
            conn.commit()
print("... Données de 'Stations.csv' chargées. \n")



## ======== Création de la table moyennes_journalieres =====================================================================
print("Création de la base de données 'moyennes_journalieres' ...")
c.execute('''DROP TABLE IF EXISTS moyennes_journalieres''')
c.execute('''CREATE TABLE moyennes_journalieres      \
              ( X REAL,                         \
                Y REAL,                         \
                nom_dept TEXT,                       \
                nom_com TEXT,                   \
                insee_com TEXT,               \
                nom_station TEXT  ,               \
                code_station TEXT  ,               \
                typologie TEXT,                      \
                influence TEXT,                \
                nom_poll TEXT,                \
                polluant_court TEXT,                 \
                id_poll_ue INT,                 \
                valeur REEL,                 \
                unite TEXT,                 \
                metrique TEXT,                 \
                date_debut TEXT,                 \
                date_fin TEXT,                 \
                validite TEXT,                 \
                x_wgs84 REEL,                 \
                y_wgs84 REEL,                 \
                x_reglementaire INT,                 \
                y_reglementaire INT,                 \
                OBJECTID INT PRIMARY KEY  )''')
print("... Base de données 'moyennes_journalieres ' créée. \n")


print("Chargement des données de 'moyennes_journalieres.csv' ...")
with open('moyennes_journalieres.csv', newline='') as csvfile :
    lecturefichier = csv.reader(csvfile, delimiter=',', quotechar='"')
    premiereligne = True
    for row in lecturefichier :
        if premiereligne :
            premiereligne = False
        else :
            c.execute('INSERT INTO moyennes_journalieres  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?)', tuple(v for v in row))
            conn.commit()
print("... Données de 'moyennes_journalieres.csv' chargées. \n")

