# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 08:31:20 2023


"""
# import plotly.graph_objects as go
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json

import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as pltd

import sqlite3

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
        stations = [("A7 SUD LYONNAIS","blue"),
                   ("A7 Salaise Ouest","green"),
                   ("A7 Valence Est","cyan"),
                   ("ANNECY Rocade","red"),
                   ("ANNEMASSE",'orange'),
                   ("Aiguille du Midi",'olive') ,
                   ("Albertville","blue"),
                   ("Aurillac-Lagarde","green"),
                   ("BOSSONS","cyan"),
                   ("Beaulieu","red"),
                   ("Bourg-en-Bresse",'orange'),
                   ("Bourgoin-Jallieu",'olive') ,
                   ("CHAMBERY BISSY","blue"),
                   ("CHAMBERY LE HAUT","green"),
                   ("CHAMONIX","cyan"),
                   ("COTIERE AIN","red"),
                   ("Chamalières Europe",'orange'),
                   ("Chambéry Trafic",'olive') ,
                   ("Champ sur Drac","blue"),
                   ("Drôme Rurale Sud-SND","green"),
                   ("Edouard Michelin","cyan"),
                   ("Esplanade Gare","red"),
                   ("FEYZIN STADE",'orange'),
                   ("GAILLARD",'olive') ,
                   ("GERLAND","blue"),
                   ("Grenoble Boulevards","green"),
                   ("Grenoble Les Frenes","cyan"),
                   ("Grenoble PeriurbSud","red"),
                   ("Gresivaudan Periurb",'orange'),
                   ("HAUT BEAUJOLAIS",'olive') ,
                   ("Jardin Lecoq","blue"),
                   ("LA TALAUDIERE","green"),
                   ("LOVERCHY","cyan"),
                   ("LYON Centre","red"),
                   ("LYON TRAFIC JAURES",'orange'),
                   ("La Léchère",'olive') ,
                   ("Le Casset2","blue"),
                   ("Le Puy-Causans","green"),
                   ("Leclanche","cyan"),
                   ("Les Ménuires","red"),
                   ("Les_Ancizes",'orange'),
                   ("Lyon - Tunnel Croix-Rousse - Sortie Rhône",'olive') ,
                   ("Lyon Périphérique","blue"),
                   ("Maurienne trafic","green"),
                   ("Montferrand","cyan"),
                   ("Montluçon","red"),
                   ("Moulins Centre",'orange'),
                   ("Métro_SaxeGambetta",'olive') ,
                   ("NOVEL","blue"),
                   ("PASSY","green"),
                   ("PASTEUR","cyan"),
                   ("Paray le Fresil","red"),
                   ("Pays du Mezenc",'orange'),
                   ("Plateau de Bonnevaux","blue"),
                   ("RIVE DE GIER","green"),
                   ("ROANNE","cyan"),
                   ("ROCHES DE CONDRIEU","red"),
                   ("ROUSSILLON",'orange'),
                   ("Rageade",'olive') ,
                   ("Riom Périurbaine","blue"),
                   ("RocadeSud_Eybens","green"),
                   ("Romans-sur-Isère","cyan"),
                   ("Royat Périurbaine","red"),
                   ("SAINT ETIENNE SUD",'orange'),
                   ("SAINT EXUPERY",'olive') ,
                   ("SAINT JEAN","blue"),
                   ("SAINT-CHAMOND","green"),
                   ("ST ETIENNE BD URBAIN","cyan"),
                   ("ST FONS CENTRE","red"),
                   ("Sablons",'orange'),
                   ("Saint Bauzile CECA",'olive') ,
                   ("Sallanches Régie","blue"),
                   ("Site autoroutier A71","green"),
                   ("Sommet du Puy de Dom","cyan"),
                   ("St GermainRhône","red"),
                   ("St Martin dHeres",'orange'),
                   ("TERNAY",'olive') ,
                   ("VAULX EN VELIN","blue"),
                   ("VENISSIEUX Village","green"),
                   ("VERNAISON","cyan"),
                   ("Valence Périurb. Sud","red"),
                   ("Valence Urb. Centre",'orange'),
                   ("Vichy",'olive') ,
                   ("Villefranche Centre","blue"),
                   ("Voiron Urbain","green")
                   ]
        title = 'Pollution atmosphérique (en µg/m³)'
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
    
    
    # # configuration du tracé
    plt.figure(figsize=(18,6))
   # plt.ylim(-5,100)
    plt.grid(which='major', color='#888888', linestyle='-')
    plt.grid(which='minor',axis='x', color='#888888', linestyle=':')
    
    ax = plt.subplot(111)
    loc_major = pltd.YearLocator()
    loc_minor = pltd.MonthLocator()
    ax.xaxis.set_major_locator(loc_major)
    ax.xaxis.set_minor_locator(loc_minor)
    format_major = pltd.DateFormatter('%B %Y')
    ax.xaxis.set_major_formatter(format_major)
    ax.xaxis.set_tick_params(labelsize=10)
    #fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
        # Configuration du tracé
   # fig, ax = plt.subplots(figsize=(15, 5))
   # ax.grid(which='major', color='#888888', linestyle='-')
   # ax.grid(which='minor', axis='x', color='#888888', linestyle=':')
   # loc_major = pltd.YearLocator()
   # loc_minor = pltd.MonthLocator()
    #ax.xaxis.set_major_locator(loc_major)
   # ax.xaxis.set_minor_locator(loc_minor)
   # format_major = pltd.DateFormatter('%B %Y')
   # ax.xaxis.set_major_formatter(format_major)
    #ax.xaxis.set_tick_params(labelsize=10)
    
    # Suppression des bandes blanches
   # fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    #fig.tight_layout()  # Ajustement automatique des marges

    # Affichage de la figure
    plt.show()
        
    # boucle sur les stations
    for station in (stations) :
        c.execute("SELECT * FROM 'moyennes_journalieres' WHERE nom_station=? ORDER BY date_debut",(station[0],))
        r = c.fetchall()
        
        # recupération de la date (1ère colonne) et transformation dans le format de pyplot
        x = [pltd.date2num(dt.date(int(a[15][:4]),int(a[15][5:7]),int(a[15][8:10]))) for a in r if not (a[15] == ('',) or  a[15]==(None,))]
        
        # récupération de la pollution (13e colonne)
        y = [float(a[12]) for a in r if not (a[12] == ('',) or  a[12]==(None,))]
        
        # tracé de la courbe
        plt.plot_date(x,y,linewidth=0.05, linestyle=':', color=station[1], label=station[0], marker='.', markersize='1.5')
        
    # légendes
    plt.legend(loc='lower left')
    plt.title('Pollution atmosphérique en Auvergne-Rhônes-Alpes',fontsize=16)
    plt.ylabel('Pollution atmosphérique (en µg/m³)')
    plt.xlabel('Date')
    plt.plot(x,y,linewidth=0.2, linestyle='-', color=station[1], label=station[0])
    # génération des courbes dans un fichier PNG
    fichier = 'courbes/pollution_'+self.path_info[1] +'.png'
    plt.savefig('client/{}'.format(fichier))

    #html = '<img src="/{}?{}" alt="pollution {}" width="100%">'.format(fichier,self.date_time_string(),self.path)
    body = json.dumps({
            'title': 'Pollution atmosphérique '+self.path_info[1], \
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
httpd = socketserver.TCPServer(("", 8014), RequestHandler)
httpd.serve_forever()

