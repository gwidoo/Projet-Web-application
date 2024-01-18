# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 08:31:20 2023


"""
# import plotly.graph_objects as go
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json
from datetime import datetime , timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sqlite3

def generate_date(start_date,end_date):
    date_list=[]
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  #
  # On surcharge la méthode qui traite les requêtes GET
  #
  def do_GET(self):

    # On récupère les étapes du chemin d'accès
    self.init_params()

    # le chemin d'accès commence par /time
    if self.path_info[0] == 'time':
      self.send_time()
   
     # le chemin d'accès commence par /regions
    elif self.path_info[0] == 'Stations':
      self.send_stations()
      
    # le chemin d'accès commence par /ponctualite
    elif self.path_info[0] == 'pollution':
      self.send_pollution()
      
    # ou pas...
    else:
      self.send_static()

  #
  # On surcharge la méthode qui traite les requêtes HEAD
  #
  def do_HEAD(self):
    self.send_static()

  #
  # On envoie le document statique demandé
  #
  def send_static(self):

    # on modifie le chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
  
  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
      elif ctype == 'application/json' :
        self.params = json.loads(self.body)
    else:
      self.body = ''
   
    # traces
    print('info_path =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)
    
  #
  # On envoie un document avec l'heure
  #
  def send_time(self):
    
    # on récupère l'heure
    time = self.date_time_string()
    # on génère un document au format html
    body = '<!doctype html>' + \
           '<meta charset="utf-8">' + \
           '<title>l\'heure</title>' + \
           '<div>Voici l\'heure du serveur :</div>' + \
           '<pre>{}</pre>'.format(time)

    # pour prévenir qu'il s'agit d'une ressource au format html
    headers = [('Content-Type','text/html;charset=utf-8')]

    # on envoie
    self.send(body,headers)

  #
  # On génère et on renvoie la liste des régions et leur coordonnées (version TD3, §5.1)
  #
  def send_stations(self):

    conn = sqlite3.connect('pollution.sqlite')
    c = conn.cursor()
    
    c.execute("SELECT DISTINCT label, X,  Y FROM 'stations'")
    r = c.fetchall()
    
    headers = [('Content-Type','application/json')];
    body = json.dumps([{'nom':nom, 'lat': lat, 'lon': lon} for (nom, lon, lat) in r])
    self.send(body,headers)

  #
  # On génère et on renvoie un graphique de ponctualite (cf. TD1)
  #
  def send_pollution(self):
    conn = sqlite3.connect('pollution.sqlite')
    c = conn.cursor()
    
    # si pas de paramètre => liste par défaut
    if len(self.path_info) <= 1 or self.path_info[1] == '' :
        # Definition des régions et des couleurs de tracé
        print('Erreur')
        self.send_error(404)
        return None
    else:
        # On teste que la région demandée existe bien
        c.execute("SELECT DISTINCT label FROM 'stations'")
        r = c.fetchall()

        # Rq: r est une liste de tuples
        if (self.path_info[1],) in r:
          stations = [(self.path_info[1],"blue")]
          title = 'Pollution atmosphérique (en µg/m³) à la station {}'.format(self.path_info[1])

        # Région non trouvée -> erreur 404
        else:
            print('Erreur nom')
            self.send_error(404)
            return None
    deb=datetime(int(self.path_info[2][:4]),int(self.path_info[2][5:7]),int(self.path_info[2][8:10]))
    fin=datetime(int(self.path_info[3][:4]),int(self.path_info[3][5:7]),int(self.path_info[3][8:10]))

    x=generate_date(deb,fin)   
    y=[[],[],[],[],[],[],[],[],[]]
    poll=['Benzène','Monoxyde de Carbone','Oxydes d Azote','Monoxyde d Azote','Dioxyde d Azote','Ozone','Dioxyde de Souffre','PM10','PM2.5']
    couleur=['blue','green','red','cyan','magenta','yellow','black','white','purple']
    # boucle sur les stations
    for station in stations :
        if self.path_info[4]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='C6H6' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[0].append(float(b))
        if self.path_info[5]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='C0' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[1].append(float(b))
        if self.path_info[6]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='NOX' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[2].append(float(b))
        if self.path_info[7]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='NO' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[3].append(float(b))           
        if self.path_info[8]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='N02' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[4].append(float(b))
        if self.path_info[9]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='O3' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[5].append(float(b))
        if self.path_info[10]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='SO2' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[6].append(float(b))
        if self.path_info[11]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='PM10' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[7].append(float(b))
        if self.path_info[12]=='oui':
            c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? AND polluant_court='PM25' ORDER BY date_debut",(station[0],))
            r = c.fetchall()
            for a in r:
                (b,)=a[12]
                (c,)=a[15]
                (d,)=a[16]
                date_d=datetime(int(c[:4]),int(c[5:7]),int(c[8:10]))
                date_f=datetime(int(d[:4]),int(d[5:7]),int(d[8:10]))
                if date_d>=deb and date_f<=fin and a[12] != ('',) and  a[12]!=(None,):
                    y[8].append(float(b))
        # recupération de la date (1ère colonne) et transformation dans le format de pyplot
        
        # récupération de la pollution (13e colonne)
                
        #y = [float(a[12]) for a in r if not (a[12] == ('',) or  a[12]==(None,))]
        


        # Rotation des étiquettes de date pour une meilleure lisibilité
        

    # légendes
    plt.title('Pollution atmosphérique à {}'.format(station[0]),fontsize=16)
    plt.ylabel('Pollution atmosphérique (en µg/m³)')
    plt.xlabel('Date')
    for i in range(4,13):
        if self.path_info[i]=='oui':
            plt.plot(x,y[i-4],color=couleur[i-4], label=poll[i-4])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    plt.legend(loc='lower left')
    plt.show()
    
    
    
    # génération des courbes dans un fichier PNG
    fichier = 'courbes/pollution_'+self.path_info[1] +'.png'
    plt.savefig('client/{}'.format(fichier))

    #html = '<img src="/{}?{}" alt="pollution {}" width="100%">'.format(fichier,self.date_time_string(),self.path)
    body = json.dumps({
            'title': 'Pollution atmosphérique '+self.path_info[1:], \
            'img': '/'+fichier \
             });
    # on envoie
    headers = [('Content-Type','application/json')];
    self.send(body,headers)

            
    
  #
  # On envoie les entêtes et le corps fourni
  #
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    # on envoie la ligne de statut
    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(encoded)

 
#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8042), RequestHandler)
httpd.serve_forever()

