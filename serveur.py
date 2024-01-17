# import plotly.graph_objects as goimport http.serverimport socketserverfrom urllib.parse import urlparse, parse_qs, unquoteimport jsonimport matplotlib.pyplot as pltimport datetime as dtimport matplotlib.dates as pltdimport sqlite3################################################################################# numéro du port TCP utilisé par le serveurport_serveur = 8000# Classe dérivée pour traiter les requêtes entrantes du serveur#class RequestHandler(http.server.SimpleHTTPRequestHandler):      # nom du serveur  server_version = "serveur.py"  # sous-répertoire racine des documents statiques  static_dir = '/client'  #  # Surcharge du constructeur pour imposer 'client' comme sous-répertoire racine    # On surcharge la méthode qui traite les requêtes GET  #  def do_GET(self):    # On récupère les étapes du chemin d'accès    self.init_params()    # le chemin d'accès commence par /time    if self.path_info[0] == 'time':      self.send_time()        # le chemin d'accès commence par /stations    elif self.path_info[0] == 'Stations':      self.send_stations()          # le chemin d'accès commence par /pollution    elif self.path_info[0] == 'pollution':      self.send_pollution()          # ou pas...    else:      self.send_static()              #  # On surcharge la méthode qui traite les requêtes HEAD  #  def do_HEAD(self):    self.send_static()          #  # On envoie le document statique demandé  #  def send_static(self):    # on modifie le chemin d'accès en insérant un répertoire préfixe    self.path = self.static_dir + self.path    # on appelle la méthode parent (do_GET ou do_HEAD)    # à partir du verbe HTTP (GET ou HEAD)    if self.command == 'HEAD':            # Si la requête est HEAD, on envoie uniquement les entêtes            self.send_response(200)            headers = self.get_headers()            [self.send_header(*t) for t in headers]            self.end_headers()    else:            # Sinon, on appelle la méthode parente (do_GET) pour traiter la requête complète            http.server.SimpleHTTPRequestHandler.do_GET(self)          def get_headers(self):        # Vous pouvez personnaliser cette fonction pour ajouter des entêtes supplémentaires si nécessaire        return [('Content-Type', 'text/html;charset=utf-8'), ('Custom-Header', 'Valeur personnalisée')]                  #       # on analyse la requête pour initialiser nos paramètres  #  def init_params(self):    # analyse de l'adresse    info = urlparse(self.path)    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]    self.query_string = info.query    self.params = parse_qs(info.query)    # récupération du corps    length = self.headers.get('Content-Length')    ctype = self.headers.get('Content-Type')    if length:      self.body = str(self.rfile.read(int(length)),'utf-8')      if ctype == 'application/x-www-form-urlencoded' :         self.params = parse_qs(self.body)      elif ctype == 'application/json' :        self.params = json.loads(self.body)    else:      self.body = ''       # traces    print('info_path =',self.path_info)    print('body =',length,ctype,self.body)    print('params =', self.params)      #  # On envoie un document avec l'heure  #  def send_time(self):        # on récupère l'heure    time = self.date_time_string()    # on génère un document au format html    body = '<!doctype html>' + \           '<meta charset="utf-8">' + \           '<title>l\'heure</title>' + \           '<div>Voici l\'heure du serveur :</div>' + \           '<pre>{}</pre>'.format(time)    # pour prévenir qu'il s'agit d'une ressource au format html    headers = [('Content-Type','text/html;charset=utf-8')]    # on envoie    self.send(body,headers)      #  # On génère et on renvoie la liste des régions et leur coordonnées (version TD3, §5.1)  #  def send_stations(self):    conn = sqlite3.connect('pollution.sqlite')    c = conn.cursor()        c.execute("SELECT DISTINCT label, X, Y FROM 'stations'")    r = c.fetchall()        headers = [('Content-Type','application/json')];    body = json.dumps([{'nom':nom, 'lat': lat, 'lon': lon} for (nom, lon, lat) in r])    self.send(body,headers)      def send_pollution(self,nom_station, start_date, end_date):    conn = sqlite3.connect('pollution.sqlite')    c = conn.cursor()        c.execute("SELECT nom_polluant, valeur, unite  FROM 'moyennes_journalieres' WHERE nom_station = 'nom_station' AND date_debut = 'start_date' AND date_fin = 'end_date'")    r = c.fetchall()        headers = [('Content-Type','application/json')];    body = json.dumps([{'nom du polluant':nom_polluant, 'valeur de la mesure': val, 'unite': unite} for (nom_polluant, val, unite) in r])    self.send(body,headers)      #  # On envoie les entêtes et le corps fourni  #  def send(self,body,headers=[]):    # on encode la chaine de caractères à envoyer    encoded = bytes(body, 'UTF-8')    # on envoie la ligne de statut    self.send_response(200)    # on envoie les lignes d'entête et la ligne vide    [self.send_header(*t) for t in headers]    self.send_header('Content-Length',int(len(encoded)))    self.end_headers()    # on envoie le corps de la réponse    self.wfile.write(encoded)################################################################################# Instanciation et lancement du serveur#httpd = socketserver.TCPServer(("", 8080), RequestHandler)httpd.serve_forever()