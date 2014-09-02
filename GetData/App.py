# -*- coding: <utf-8> -*-
import bottle
import sqlite3
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib # računanje MD5 kriptografski hash za gesla
import datetime


# KONFIGURACIJA
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database='seminarska_matjazz', host='audrey.fmf.uni-lj.si', user='matjazz', password='marmelada')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
TrenutniDatum = datetime.datetime.now()
TrenutnoLeto = TrenutniDatum.year

# Static Routes
@bottle.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root='static/js')

@bottle.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    f = filename.split('/')
    filename = f[-1]
    return bottle.static_file(filename, root='static/css')

@bottle.get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root='static/img')

@bottle.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename, root='static/fonts')

# Ostalo

# Skrivnost za kodiranje cookijev
secret = "travažgečkapodplate87ztszfg8ez78"

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


# Funkcija, ki v cookie spravi sporocilo
def set_sporocilo(tip, vsebina):
    bottle.response.set_cookie('message', (tip, vsebina), path='/', secret=secret)


# Funkcija, ki iz cookija dobi sporočilo, če je
def get_sporocilo():
    sporocilo = bottle.request.get_cookie('message', default=None, secret=secret)
    bottle.response.delete_cookie('message')
    return sporocilo


def get_user(auto_login = True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT uporabnisko_ime, ime, priimek, geslo FROM glasbenik WHERE uporabnisko_ime=%s",
                  (username,))
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    if auto_login:
        bottle.redirect('/login')
    else:
        return None

def sem_prijavljen(auto_login = True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT uporabnisko_ime FROM glasbenik WHERE uporabnisko_ime=%s",
                  (username,))
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
        
    # Če pridemo do sem, uporabnik ni prijavljen
    else:
        return None


@bottle.route('/')
@bottle.get('/')
def main(sporocila=[]):
    cur.execute("SELECT * FROM prijavljen_je;")
    prijavljen_uporime = cur.fetchone()[0]
    
    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    uporabnik = cur.fetchall()
    
    cur.execute("SELECT ime FROM obcina ORDER BY ime")
    CurObcina = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurZanr = cur.fetchall()
    
    cur.execute("SELECT stopnja FROM stopnja_znanja")
    CurStopnja = cur.fetchall()
    
    cur.execute("SELECT spol FROM spol")
    CurSpol = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurZanr2 = cur.fetchall()
    
    cur.execute("SELECT ime FROM obcina ORDER BY ime")
    CurObcina2 = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurIsce = cur.fetchall()

    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    CurIsce2 = cur.fetchall()
    
    return bottle.template('main.html', uporabnik=uporabnik, obcina=CurObcina, zanr=CurZanr,
                   stopnja=CurStopnja, spol=CurSpol, zanr2=CurZanr2,
                   obcina2=CurObcina2, isce = CurIsce, isce2 = CurIsce2, sporocila = sporocila, prijavljen_uporime = prijavljen_uporime)


@bottle.post('/iskanjeglasbenika')
def iskanje():
    cur.execute("SELECT * FROM prijavljen_je;")
    prijavljen_uporime = cur.fetchone()[0]
    
    instrument = bottle.request.forms.getunicode('instrument')
    obcina = bottle.request.forms.getunicode('obcina')
    zanr = bottle.request.forms.getunicode('zanr')
    stopnja = bottle.request.forms.getunicode('stopnja')
    spol = bottle.request.forms.getunicode('spol')
    isceskupino = bottle.request.forms.getunicode('isce')

    zadetki = (instrument, obcina, zanr, stopnja, spol, isceskupino)
    
    select_stavek = """SELECT DISTINCT uporabnisko_ime, ime, priimek, spol, e_mail, glasbilo, stopnja_znanja, 
        leto_zacetka, obcina, igra_zanr, zanr AS isce_skupino_ki_igra FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime WHERE"""

    if zadetki[0] != None:
        select_stavek = select_stavek+" glasbilo = %s AND"
    if zadetki[1] != None:
        select_stavek = select_stavek+" obcina = %s AND"
    if zadetki[2] != None:
        select_stavek = select_stavek+" igra_zanr = %s AND"    
    if zadetki[3] != None:
        select_stavek = select_stavek+" stopnja_znanja = %s AND"
    if zadetki[4] != None:
        select_stavek = select_stavek+" spol = %s AND"
    if zadetki[5] != None:
        select_stavek = select_stavek+" zanr = %s AND"
    #if zadetki[0] != None or zadetki[1] != None or zadetki[2] != None or zadetki[3] != None or zadetki[4] != None or zadetki[5] != None:
    #    select_stavek = select_stavek+" TRUE"
    select_stavek = select_stavek+" TRUE"

    parametri = []
    for i in zadetki:
        if i != None:
            parametri.append(i)
    parametri = tuple(parametri)

    cur.execute(select_stavek, (parametri))
    CurIskanjeGlasbenika = cur.fetchall()
    
    return bottle.template('iskanjeglasbenika.html', IskanjeGlasbenika = CurIskanjeGlasbenika, prijavljen_uporime = prijavljen_uporime)


@bottle.post('/iskanjeskupine')
def iskanje():
    cur.execute("SELECT * FROM prijavljen_je;")
    prijavljen_uporime = cur.fetchone()[0]
    
    obcina2 = bottle.request.forms.getunicode('obcina2')
    zanr2 = bottle.request.forms.getunicode('zanr2')
    isce2 = bottle.request.forms.getunicode('isce2')

    zadetki = (obcina2, zanr2, isce2)

    select_stavek = """SELECT DISTINCT ime, datum_ustanovitve, spletna_stran, fb, obcina, igra_zanr, glasbilo, spol, stevilo FROM skupina
        LEFT JOIN skupina_deluje_v_okolici ON skupina.ime = skupina_deluje_v_okolici.skupina
        LEFT JOIN skupina_igra_zanr ON skupina.ime = skupina_igra_zanr.skupina
        LEFT JOIN skupina_isce ON skupina.ime = skupina_isce.skupina
        WHERE"""
    
    if zadetki[0] != None:
        select_stavek = select_stavek+" obcina = %s AND"
    if zadetki[1] != None:
        select_stavek = select_stavek+" igra_zanr = %s AND"
    if zadetki[2] != None:
        select_stavek = select_stavek+" glasbilo = %s AND"    
    select_stavek = select_stavek+" TRUE"
    
    parametri = []
    for i in zadetki:
        if i != None:
            parametri.append(i)
    parametri = tuple(parametri)

    cur.execute(select_stavek, (parametri))
    CurIskanjeSkupine = cur.fetchall()
    
    return bottle.template('iskanjeskupine.html', IskanjeSkupine = CurIskanjeSkupine, prijavljen_uporime = prijavljen_uporime)


@bottle.get('/login')
@bottle.route('/login')
@bottle.route('/login/')
def login_get():
    """Serviraj formo za login."""
    return bottle.template('login.html',napaka=None,uporime=None)

@bottle.get("/logout/") # naslov na katerem ti pobriše kuki in te vrže na glavno stran
def logout():
    """Pobriši cookie in preusmeri na glavno stran."""
    prijavljen_uporime = None
    cur.execute("UPDATE prijavljen_je SET uporabnik = %s", (prijavljen_uporime,))
    bottle.response.delete_cookie(key='username', secret=secret, path='/')
    
    bottle.redirect('/login')


@bottle.post("/login")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.getunicode('uporime')
   
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.getunicode('geslo'))
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur.execute("UPDATE prijavljen_je SET uporabnik = %s", (username,))
    
    cur.execute("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s AND geslo=%s",
              (username, password))
    CurVpis = cur.fetchone()
    
    if CurVpis is None:
        # Username in geslo se ne ujemata
        return bottle.template("login.html",
                               napaka="Nepravilna prijava",
                               uporime=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie('username', username, secret=secret, path='/')
        prijavljen_uporime = username
        bottle.redirect("/uporabnik/"+username) 



@bottle.post('/noviuporabnik')
@bottle.route('/noviuporabnik')
@bottle.route('/noviuporabnik/')
# servira formo za signin
def noviuporabnik():
    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    glasbilo = cur.fetchall()
    
    cur.execute("SELECT ime FROM obcina ORDER BY ime")
    CurObcina = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurZanr = cur.fetchall()
    
    cur.execute("SELECT stopnja FROM stopnja_znanja")
    CurStopnja = cur.fetchall()
    
    cur.execute("SELECT spol FROM spol")
    CurSpol =  cur.fetchall()

    MoznaLeta = [i for i in range(TrenutnoLeto-90, TrenutnoLeto+1)]
    
    return bottle.template('signin.html', glasbilo=glasbilo, obcina=CurObcina, zanr=CurZanr,
                           stopnja=CurStopnja, spol=CurSpol, napaka=None, uporime=None,
                           ime1=None, priimek1=None, mail1=None, letorojstva=None, MoznaLeta = MoznaLeta)
   

@bottle.route('/uporabnik/:uporime_stran')
@bottle.route('/uporabnik/:uporime_stran/')
@bottle.route('/uporabnik/<uporime_stran>/')
@bottle.route('/uporabnik/<uporime_stran>')
def uporabnikova_stran(uporime_stran,sporocila=[]): # v argumentu funkcije je informacija na čigavi spletni strani smo
    
    cur.execute("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s", (uporime_stran,))
    if cur.fetchone() is None:
        return "Uporabnik ne obstaja"

    # Kdo je prijavljeni uporabnik? 
    (uporime_login, ime_login, priimek_login, geslo_login) = get_user()
    dolzina = len(password_md5(geslo_login)) - 10

    cur.execute("SELECT stopnja FROM stopnja_znanja") # dropdown meni 'izurjenosti' za tabelo instrumentov
    CurStopnja = cur.fetchall()
    
    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime") # dropdown meni glasbil za tabelo instrumentov
    glasbilo = cur.fetchall()
    
    cur.execute("SELECT ime FROM obcina ORDER BY ime") # dropdown meni obcin za tabelo obcin
    CurObcina = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime") # dropdown meni za iskane zanre
    CurZanrDropdown1 = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime") # dropdown meni za igrane zanre
    CurZanrDropdown2 = cur.fetchall()
    
    cur.execute("SELECT spol FROM spol") # dropdown meni za spol (sprememba spola)
    CurSpolDropdown = cur.fetchall()
    
    # podatki o igranih instrumentih
    cur.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime_stran,))
    CurTabelaInstrumentov = cur.fetchall()
    
    # podatki o obcini
    cur.execute("SELECT obcina FROM glasbenik_deluje_v_okolici WHERE glasbenik = %s ", (uporime_stran,))
    CurObcinaDelovanja = cur.fetchall()
    
    # podatki o igranih zanrih
    cur.execute("SELECT igra_zanr FROM glasbenik_igra_zanr WHERE glasbenik = %s ", (uporime_stran,))
    CurZanr = cur.fetchall()
    
    # podatki o iskanih zanrih
    cur.execute("SELECT zanr FROM glasbenik_isce_skupino WHERE glasbenik = %s ", (uporime_stran,))
    CurZanr2 = cur.fetchall()

    # osebni podatki
##    cur.execute("""SELECT DISTINCT ime, priimek, e_mail, leto_rojstva, uporabnisko_ime, spol, obcina, igra_zanr, zanr FROM glasbenik
##        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
##        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
##        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
##        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
##        WHERE uporabnisko_ime = %s""", (uporime_stran,))
    cur.execute("""SELECT DISTINCT ime, priimek, e_mail, leto_rojstva, uporabnisko_ime, spol FROM glasbenik
    WHERE uporabnisko_ime = %s""", (uporime_stran,))
    CurUporabnik = cur.fetchall()

    cur.execute("SELECT skupina FROM clani_skupine WHERE clan = %s", (uporime_stran,) )
    CurIgraneSkupine = cur.fetchall()

    MoznaLeta = [i for i in range(TrenutnoLeto-90, TrenutnoLeto+1)]

    return bottle.template('uporabnik.html',
                           uporime1=uporime_stran,
                           uporime2=uporime_login,
                           TabelaInstrumentov=CurTabelaInstrumentov,
                           ObcinaDelovanja=CurObcinaDelovanja,
                           MoznaLeta = MoznaLeta,
                           IgranZanr=CurZanr,
                           IskanZanr=CurZanr2,
                           Uporabnik=CurUporabnik,
                           dolzina = dolzina,
                           sporocila=sporocila,
                           znanje=CurStopnja,
                           glasbilo=glasbilo,
                           obcina=CurObcina,
                           zanr1=CurZanrDropdown1,
                           zanr2=CurZanrDropdown2,
                           spol=CurSpolDropdown,
                           CurIgraneSkupine = CurIgraneSkupine)


@bottle.post("/uporabnik/<uporime_stran>")
@bottle.post("/uporabnik/<uporime_stran>/")
def uporabnik_change(uporime_stran):

    """Obdelaj formo za spreminjanje podatkov o uporabniku."""
   
    # Kdo je prijavljen?
    (uporime_login, ime_login, priimek_login, geslo_login) = get_user()
    
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    
    # Brisanje podatkov
    if 'delete' in bottle.request.POST.keys():
        #element_izbris = bottle.request.POST['delete'] # ne bere šumnikov
        element_izbris=bottle.request.forms.getunicode('delete')
        #input forma v html mora bit v "", sicer ignorira celotne besedne zveze-prebere le prvo besedo iz besedne zveze

        # število na začetku elementa izbrisa nam pove, kateri podatek želimo zbrisati. Pokaže nam pravo tabelo
        # Legenda: 1-igrana glasbila, 2-obcina delovanja, 3-igran zanr, 4-iskan zanr
        
        if element_izbris[0]=='1':
            glasbilo=element_izbris[1:]

            cur.execute('DELETE FROM igra_poje WHERE glasbenik = %s AND glasbilo = %s', (uporime_login, glasbilo))
            sporocila.append(("alert-warning", "Izbrisali ste glasbilo."))
            
        elif element_izbris[0]=='2':
            obcina=element_izbris[1:]

            cur.execute('DELETE FROM glasbenik_deluje_v_okolici WHERE glasbenik = %s AND obcina = %s', (uporime_login, obcina))
            sporocila.append(("alert-warning", "Izbrisali ste obcino."))
            
        elif element_izbris[0]=='3':
            IgraZanr=element_izbris[1:]
            
            cur.execute('DELETE FROM glasbenik_igra_zanr WHERE glasbenik = %s AND igra_zanr = %s', (uporime_login, IgraZanr))
            sporocila.append(("alert-warning", "Izbrisali ste igran zanr."))
            
        elif element_izbris[0]=='4':
            IsceZanr=element_izbris[1:]

            cur.execute('DELETE FROM glasbenik_isce_skupino WHERE glasbenik = %s AND zanr = %s', (uporime_login, IsceZanr))            
            sporocila.append(("alert-warning", "Izbrisali ste iskan zanr."))
        
        return uporabnikova_stran(uporime_stran, sporocila=sporocila)

    # SPREMINJANJE OSEBNIH PODATKOV
    
    # Novo ime
    ime_new = bottle.request.forms.getunicode('ime_novo')
    # Nov priimek
    priimek_new = bottle.request.forms.getunicode('priimek_nov')
    # Nov email
    email_new = bottle.request.forms.getunicode('email_nov')
    # Popravljena letnica rojstva
    lrojstva_new = bottle.request.forms.getunicode('lrojstva_nova')
    # Novo uporabniško ime
    uporime_new = bottle.request.forms.getunicode('uporime_novo')
    # Novo geslo
    geslo_new1 = bottle.request.forms.getunicode('geslo_novo1')
    geslo_new2 = bottle.request.forms.getunicode('geslo_novo2')
    # Nov Spol
    spol_new = bottle.request.forms.getunicode('spol_nov')
    """
    # Spremenjena občina delovanja
    obcina_new = bottle.request.forms.getunicode('obcina_nova')
    """
    
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s",(uporime_login,))
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    if (ime_new or priimek_new or email_new or lrojstva_new or uporime_new or geslo_new1 or geslo_new2 or spol_new)!= None:
        if cur.fetchone():
            
            # Geslo je ok
            # Ali je treba spremeniti ime?
            if ime_new != '':
                cur.execute("UPDATE glasbenik SET ime=%s WHERE uporabnisko_ime=%s", (ime_new, uporime_login))
                
                sporocila.append(("alert-success", "Spremenili ste si ime."))
            if priimek_new != '':
                cur.execute("UPDATE glasbenik SET priimek=%s WHERE uporabnisko_ime=%s", (priimek_new, uporime_login))
                
                sporocila.append(("alert-success", "Spremenili ste si priimek."))
            if email_new != '':
                cur.execute("UPDATE glasbenik SET e_mail=%s WHERE uporabnisko_ime=%s", (email_new, uporime_login))
                
                sporocila.append(("alert-success", "Spremenili ste si email."))
            if lrojstva_new != '' and lrojstva_new != None:
                cur.execute("UPDATE glasbenik SET leto_rojstva=%s WHERE uporabnisko_ime=%s", (lrojstva_new, uporime_login))

                sporocila.append(("alert-success", "Spremenili ste leto rojstva."))

            if uporime_new!= '':
                cur.execute("UPDATE glasbenik SET uporabnisko_ime=%s WHERE uporabnisko_ime=%s" , (uporime_new, uporime_login))
                uporime_stran = uporime_new
                sporocila.append(("alert-success", "Spremenili ste uporabniško ime."))
                ## TUKAJ TE PREUSMERI NA GLAVNI PAGE

            if spol_new!= None:
                cur.execute("UPDATE glasbenik SET spol=%s WHERE uporabnisko_ime=%s", (spol_new, uporime_login))
                
                sporocila.append(("alert-success", "Spremenili ste si spol.")) 
            # Ali je treba spremeniti geslo?

            if geslo_new1 or geslo_new2:
                # Preverimo, ali se gesli ujemata
                if geslo_new1 == geslo_new2:
                    # Vstavimo v bazo novo geslo
                    geslo_new1 = password_md5(geslo_new1)
                    cur.execute ("UPDATE glasbenik SET geslo=%s WHERE uporabnisko_ime = %s", (geslo_new1, uporime_login))
                    
                    sporocila.append(("alert-success", "Spremenili ste geslo."))
                else:
                    sporocila.append(("alert-danger", "Gesli se ne ujemata"))
        else:
            # Geslo ni ok
            sporocila.append(("alert-danger", "Ne obstajate v bazi"))
    else:


        #VSTAVLJANJE PODATKOV O DEJAVNOSTI
        
        # TABELA INSTRUMENTOV
        glasbilo = bottle.request.forms.getunicode('instrument')
        st_znanja = bottle.request.forms.getunicode('stopnja')
        leto_zac = bottle.request.forms.getunicode('leto')
        
        
        if glasbilo != None and st_znanja != None and leto_zac!= '':
            cur.execute("INSERT INTO igra_poje(glasbenik, glasbilo, stopnja_znanja, leto_zacetka) VALUES (%s,%s,%s,%s)",
                                        (uporime_login, glasbilo, st_znanja, leto_zac))
            
            sporocila.append(("alert-success", "Dodali ste glasbilo."))
           
        # TABELA OBCIN
        obcina = bottle.request.forms.getunicode('obcina')
        
        if obcina!=None:
            cur.execute("INSERT INTO glasbenik_deluje_v_okolici(glasbenik, obcina) VALUES (%s,%s)",
                                        (uporime_login, obcina))
            
            sporocila.append(("alert-success", "Dodali ste obcino."))

        # TABELA IGRANIH ZANROV
        IgraZanr = bottle.request.forms.getunicode('IgranZanr')

        if IgraZanr!=None:
            cur.execute("INSERT INTO glasbenik_igra_zanr(glasbenik, igra_zanr) VALUES (%s,%s)",
                                        (uporime_login, IgraZanr))
            
            sporocila.append(("alert-success", "Dodali ste igran žanr."))

        # TABELA ISKANIH ZANROV
        IskanZanr = bottle.request.forms.getunicode('IskanZanr')
        
        if IskanZanr!=None:
            cur.execute("INSERT INTO glasbenik_isce_skupino(glasbenik, zanr) VALUES (%s,%s)",
                                        (uporime_login, IskanZanr))
            
            sporocila.append(("alert-success", "Dodali ste iskan žanr.")) 
        

    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    return uporabnikova_stran(uporime_stran, sporocila=sporocila)


@bottle.post('/signin')
@bottle.route('/signin')
@bottle.route('/signin/')
# Obdela formo za signin
def signin():
    instrument = bottle.request.forms.getunicode('instrument')
    obcina = bottle.request.forms.getunicode('obcina')
    zanr = bottle.request.forms.getunicode('zanr')
    stopnja = bottle.request.forms.getunicode('stopnja')
    spol = bottle.request.forms.getunicode('spol')
    isceskupino = bottle.request.forms.getunicode('isceskupino')
    ime1 = bottle.request.forms.getunicode('ime1')
    priimek1 = bottle.request.forms.getunicode('priimek1')
    mail1 = bottle.request.forms.getunicode('mail1')
    letorojstva = bottle.request.forms.getunicode('letorojstva')
    uporime = bottle.request.forms.getunicode('username1')
    geslo1 = bottle.request.forms.getunicode('geslo1')
    geslo2 = bottle.request.forms.getunicode('geslo2')
    letozacetka = bottle.request.forms.getunicode('letozacetka')
    print(obcina)

    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    glasbilo = cur.fetchall()
    
    cur.execute("SELECT ime FROM obcina ORDER BY ime")
    CurObcina = cur.fetchall()
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurZanr = cur.fetchall()
    
    cur.execute("SELECT stopnja FROM stopnja_znanja")
    CurStopnja = cur.fetchall()
    
    cur.execute("SELECT spol FROM spol")
    CurSpol = cur.fetchall()
    
    cur.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime,))
    CurTabelaInstrumentov = cur.fetchall()
    
    # Ali uporabnik že obstaja?
    cur.execute("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s", (uporime,))
    CurRegistracija1 = cur.fetchone()
    
    if CurRegistracija1:
        # Uporabnik že obstaja
        return bottle.template('signin.html', glasbilo=glasbilo, obcina=CurObcina, zanr=CurZanr,
                               stopnja=CurStopnja, spol=CurSpol, napaka='To uporabniško ime je že zavzeto!',
                               ime1=ime1, priimek1=priimek1, mail1=mail1, letorojstva=letorojstva,uporime=None)
    elif not geslo1 == geslo2:
        # Geslo se ne ujemata
        return bottle.template('signin.html', glasbilo=glasbilo, obcina=CurObcina, zanr=CurZanr,
                               stopnja=CurStopnja, spol=CurSpol, napaka='Gesli se ne ujemata!',
                               uporime=uporime, ime1=ime1, priimek1=priimek1, mail1=mail1,
                               letorojstva=letorojstva)
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        #password = password_md5(password1)
        
        cur.execute("""INSERT INTO glasbenik (uporabnisko_ime, ime, priimek, spol, e_mail, leto_rojstva, geslo)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",(uporime, ime1, priimek1, spol, mail1, letorojstva, password_md5(geslo1)))

        cur.execute("""INSERT INTO igra_poje (glasbenik, glasbilo, stopnja_znanja, leto_zacetka)
                                VALUES (%s, %s, %s, %s)""", (uporime, instrument, stopnja, letozacetka))

        cur.execute("""INSERT INTO glasbenik_igra_zanr (glasbenik, igra_zanr)
                                VALUES (%s, %s)""", (uporime, zanr))

        # kaj je z žanrom pri iskanju skupine?
        #CurRegistracija.execute("""INSERT INTO glasbenik_isce_skupino (glasbenik, zanr)
                                #VALUES (%s, %s)""", (uporime, zanr))

        cur.execute("""INSERT INTO glasbenik_deluje_v_okolici (glasbenik, obcina)
                                VALUES (%s, %s)""", (uporime, obcina))
        
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', uporime, path='/', secret=secret)
        bottle.redirect("/uporabnik/"+uporime) #to je uporabil bauer-redirect
    
    #return bottle.template('uporabnik.html', uporime=uporime, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=Uporabnik)


@bottle.route('/novaskupina')
def novaskupina():
    MoznaLeta = [i for i in range(TrenutnoLeto-90, TrenutnoLeto+1)]
    return bottle.template('signinskupina.html', napaka=None, MoznaLeta = MoznaLeta)

@bottle.post('/signinskupina')
def skupinasignin():
    ime_skupine = bottle.request.forms.getunicode('imeskupine')
    leto_ust = bottle.request.forms.getunicode('letoust')
    mail_skupine = bottle.request.forms.getunicode('mailskupine')
    spletna_stran = bottle.request.forms.getunicode('webskupine')
    fb = bottle.request.forms.getunicode('fb')
    telefon = bottle.request.forms.getunicode('telefon')
    datum = leto_ust+"-01-01"
    if telefon == '' or telefon == None: telefon='000000000'

    # Kdo je prijavljeni uporabnik? 
    (uporime_login, ime_login, priimek_login, geslo) = get_user()
    
##    # Ali uporabnik že obstaja?
##    cur.execute("SELECT 1 FROM skupina WHERE ime=%s", ('banance'))
##    CurRegistracija1 = cur.fetchone()
##    print(CurRegistracija1)
##    

    # Vse je v redu, vstavi novo skupino v bazo
    cur.execute("""INSERT INTO skupina(ime, datum_ustanovitve, e_mail, spletna_stran, fb, telefonska_stevilka)
                            VALUES (%s, %s, %s, %s, %s, %s)""",(ime_skupine, datum, mail_skupine, spletna_stran, fb, telefon))

    # Pogledamo kaj igra uporabnik, ki je ustvaril skupino in vse to dodamo v tabele;
    cur.execute("SELECT glasbilo FROM igra_poje WHERE glasbenik=%s", (uporime_login,))
    Instrumenti = cur.fetchall()

    for glasbilo in Instrumenti:
        # Tisti ki ustvari skupino je avtomatično njen član
        cur.execute("""INSERT INTO clani_skupine(skupina, clan, glasbilo)
                                VALUES (%s, %s, %s)""", (ime_skupine, uporime_login, glasbilo[0]))
    sporocila = [("alert-success", "Ustvarili ste novo skupino. Dobrodolšli.")]

    return skupinska_stran(ime_skupine, sporocila=sporocila)

@bottle.route('/skupina/<:skupina_stran/')
@bottle.route('/skupina/<skupina_stran>') 
def skupinska_stran(skupina_stran,sporocila=[], parametri=[]): # v argumentu funkcije je informacija na čigavi spletni strani smo
    # preverimo ali skupina obstaja
    cur.execute("SELECT 1 FROM skupina WHERE ime=%s", (skupina_stran,))
    if cur.fetchone() is None:
        return "Skupina ne obstaja"
    
    # Kdo je prijavljeni uporabnik? 
    (uporime_login, ime_login, priimek_login, geslo) = get_user()

    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    CurGlasbilaDropdown=cur.fetchall() # dropdown meni glasbil za tabelo instrumentov

    cur.execute("SELECT ime FROM obcina ORDER BY ime")
    CurObcinaDropdown=cur.fetchall() # dropdown meni obcin za tabelo obcin
    
    cur.execute("SELECT ime FROM zanr ORDER BY ime")
    CurZanrDropdown=cur.fetchall() # dropdown meni za igrane zanre

    cur.execute("SELECT spol FROM spol") # dropdown meni za spol
    CurSpolDropdown=cur.fetchall()

    cur.execute("SELECT uporabnisko_ime FROM glasbenik") # dropdown meni za uporabnike baze
    CurUporabnikiDropdown=cur.fetchall() 
    
    cur.execute("""SELECT DISTINCT skupina, clan, glasbilo, spol FROM clani_skupine
                JOIN glasbenik ON uporabnisko_ime=clan
                WHERE skupina = %s""", (skupina_stran,))
    CurClani=cur.fetchall()

    cur.execute("SELECT skupina, clan FROM clani_skupine WHERE skupina=%s", (skupina_stran,))
    JeClan=[skupina_stran, uporime_login] in cur.fetchall() # ali je obiskovalec tudi clan skupine
    
    # podatki o iskanih članih
    cur.execute("SELECT glasbilo, spol, stevilo FROM skupina_isce WHERE skupina = %s ", (skupina_stran,))
    CurIskaniClani=cur.fetchall()
    # podatki o obcini delovanja
    cur.execute("SELECT obcina FROM skupina_deluje_v_okolici WHERE skupina = %s ", (skupina_stran,))
    CurObcinaDelovanja=cur.fetchall()
    # podatki o igranih zanrih
    cur.execute("SELECT igra_zanr FROM skupina_igra_zanr WHERE skupina = %s ", (skupina_stran,))
    CurZanr=cur.fetchall()
    
    # Osnovni podatki o skupini
    cur.execute("""SELECT ime, datum_ustanovitve, e_mail, spletna_stran, fb, telefonska_stevilka FROM skupina
        WHERE ime = %s""", (skupina_stran,))
    CurSkupina=cur.fetchall()

    MoznaLeta = [i for i in range(TrenutnoLeto-90, TrenutnoLeto+1)]
    clan_nov = None
    IzbranClan = False
    Instrumenti = []

    if parametri != []:
        clan_nov = parametri[0]
        IzbranClan = parametri[1]
        Instrumenti = parametri[2]
    
    return bottle.template('skupina.html',
                           skupina_stran=skupina_stran,
                           uporime = uporime_login,
                           Clani=CurClani,
                           JeClan=JeClan,
                           clan_nov = clan_nov,
                           IzbranClan = IzbranClan,
                           Instrumenti = Instrumenti,
                           MoznaLeta = MoznaLeta,
                           Iskani_clani=CurIskaniClani,
                           ObcinaDelovanja=CurObcinaDelovanja,
                           IgranZanr=CurZanr,
                           OsnovniSkupina=CurSkupina,
                           sporocila=sporocila,
                           Uporabniki=CurUporabnikiDropdown,
                           glasbilo=CurGlasbilaDropdown,
                           obcina=CurObcinaDropdown,
                           zanr=CurZanrDropdown,
                           spol=CurSpolDropdown)

    

@bottle.post("/skupina/<skupina_stran>")
def skupina_change(skupina_stran):

    """Obdelaj formo za spreminjanje podatkov o uporabniku."""
    # Kdo je prijavljen?
    (uporime_login, ime_login, priimek_login, geslo) = get_user()
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    parametri = []

    # Brisanje podatkov

    if 'delete' in bottle.request.POST.keys():
        #element_izbris = bottle.request.POST['delete'] # ne bere šumnikov
        element_izbris=bottle.request.forms.getunicode('delete')
        #input forma v html mora bit v "", sicer ignorira celotne besedne zveze-prebere le prvo besedo iz besedne zveze

        # število na začetku elementa izbrisa nam pove, kateri podatek želimo zbrisati. Pokaže nam pravo tabelo
        # Legenda: 1-igrana glasbila, 2-obcina delovanja, 3-igran zanr, 4-iskan zanr
        #a,b,c=element_izbris
        if element_izbris[0]=='1':
            clan=element_izbris[1:]
            split = element_izbris.split(',')
            cur.execute('DELETE FROM clani_skupine WHERE skupina = %s AND clan = %s AND glasbilo = %s', (skupina_stran, split[1], split[2]))
            sporocila.append(("alert-warning", "Vrgli ste člana iz skupine."))
            
        elif element_izbris[0]=='2':
            split=element_izbris.split(',')
            cur.execute('DELETE FROM skupina_isce WHERE skupina = %s AND glasbilo = %s AND spol = %s', (skupina_stran, split[1], split[2]))
            sporocila.append(("alert-warning", "Izbrisali ste oglas za iskanega člana."))
            
        elif element_izbris[0]=='3':
            obcina=element_izbris[1:]
            cur.execute('DELETE FROM skupina_deluje_v_okolici WHERE skupina = %s AND obcina = %s', (skupina_stran, obcina))
            sporocila.append(("alert-warning", "Izbrisali ste občino delovanja."))
            
        elif element_izbris[0]=='4':
            IgranZanr=element_izbris[1:]
            cur.execute('DELETE FROM skupina_igra_zanr WHERE skupina = %s AND igra_zanr = %s', (skupina_stran, IgranZanr))
            sporocila.append(("alert-warning", "Izbrisali ste igran zanr."))
        
        
        return skupinska_stran(skupina_stran, sporocila=sporocila)

    # SPREMINJANJE OSEBNIH PODATKOV
    #Popravljeno ime skupine
    ime_novo = bottle.request.forms.getunicode('ime_novo')
    # Popravljen datum ustanovitve
    novoleto_ust = bottle.request.forms.getunicode('novolevo_ust')
    # Nov email
    email_nov = bottle.request.forms.getunicode('email_nov')
    # Nova spletna stran
    spl_stran_nova = bottle.request.forms.getunicode('spl_stran_nova')
    # Nova fb stran
    fb_nov = bottle.request.forms.getunicode('fb_nov')
    # Nova telefnska številka
    telefon_nov = bottle.request.forms.getunicode('telefon_nov')
    
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s",(uporime_login,))
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    if (ime_novo or novoleto_ust or email_nov or spl_stran_nova or fb_nov or telefon_nov)!= None:
        if cur.fetchone():
            # Geslo je ok
            if ime_novo != '':
                cur.execute("UPDATE skupina SET ime=%s WHERE ime=%s", (ime_novo, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste si ime skupine."))
                skupina_stran = ime_novo
            if novoleto_ust != "" and novoleto_ust != None:
                datum_ustanovitve_nov = novoleto_ust +'-01-01'
                cur.execute("UPDATE skupina SET datum_ustanovitve=%s WHERE ime=%s", (datum_ustanovitve_nov, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste datum ustanovitve."))
            if email_nov != "":
                cur.execute("UPDATE skupina SET e_mail=%s WHERE ime=%s", (email_nov, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste naslov vaše elektronske pošte."))
            if spl_stran_nova != '':
                cur.execute("UPDATE skupina SET spletna_stran=%s WHERE ime=%s", (spl_stran_nova, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste naslov vaše spletne strani."))
            if fb_nov!= '':
                cur.execute("UPDATE skupina SET fb=%s WHERE ime=%s", (fb_nov, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste naslov vaše facebook strani."))
            if telefon_nov!= '':
                cur.execute("UPDATE skupina SET telefonska_stevilka=%s WHERE ime=%s", (telefon_nov, skupina_stran))
                sporocila.append(("alert-success", "Spremenili ste telefonsko številko vaše skupine."))     
        else:
            # Geslo ni ok
            sporocila.append(("alert-danger", "Ne obstajate v bazi"))

    else:
        #VSTAVLJANJE PODATKOV O DEJAVNOSTI
    
        # TABELA CLANOV
        clan_nov = bottle.request.forms.getunicode('clan_nov')   
        if clan_nov != None:
            IskanClan = True
            igraninstrument = bottle.request.forms.get('igraninstrument')
            if igraninstrument != None:
                cur.execute("""INSERT INTO clani_skupine(skupina, clan, glasbilo)
                                    VALUES (%s, %s, %s)""", (skupina_stran, clan_nov, igraninstrument))
                sporocila.append(("alert-success", "Dodali ste člana."))

            else:
                # Pogledamo kaj igra uporabnik, ki je ustvaril skupino in vse to dodamo v tabele;
                cur.execute("SELECT glasbilo FROM igra_poje WHERE glasbenik=%s", (clan_nov,))
                Instrumenti = cur.fetchall()
                sporocila.append(("alert-info", "Izberite glasbilo, ki ga igra clan."))
                parametri = [clan_nov, IskanClan, Instrumenti]
                
            

        # TABELA ISKANIH PROFILOV
        instrument = bottle.request.forms.getunicode('iskanoglasbilo')
        spol = bottle.request.forms.getunicode('spol')
        stevilo=bottle.request.forms.getunicode('stevilo')

        if (instrument and spol and stevilo) != None:
            cur.execute("INSERT INTO skupina_isce(skupina, glasbilo, spol, stevilo) VALUES (%s, %s, %s, %s)", (skupina_stran, instrument, spol, stevilo))
            sporocila.append(("alert-success", "Dodali ste iskanega člana."))
    
        # TABELA OBCIN
        obcina = bottle.request.forms.getunicode('obcina')

        if obcina!=None:
            cur.execute("INSERT INTO skupina_deluje_v_okolici(skupina, obcina) VALUES (%s,%s)",
                        (skupina_stran, obcina))
            sporocila.append(("alert-success", "Dodali ste obcino."))

        # TABELA IGRANIH ZANROV
        IgranZanr = bottle.request.forms.getunicode('IgranZanr')

        if IgranZanr!=None:
            cur.execute("INSERT INTO skupina_igra_zanr(skupina, igra_zanr) VALUES (%s,%s)",
                        (skupina_stran, IgranZanr))
            sporocila.append(("alert-success", "Dodali ste igran žanr."))

    
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    
    return skupinska_stran(skupina_stran, sporocila=sporocila, parametri = parametri)

    
@bottle.post("/brisi/<skupina_stran>")
def skupina_change(skupina_stran):
    # Brisanje podatkov
    (uporime_login, ime_login, priimek_login, geslo) = get_user()
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    
    if 'delete' in bottle.request.POST.keys():
        cur.execute('DELETE FROM skupina WHERE ime = %s', (skupina_stran,))
        sporocila.append(("alert-danger", "Izbrisali ste skupino {0}.".format(skupina_stran)))
    return uporabnikova_stran(uporime_login,sporocila=sporocila)

@bottle.post("/brisi/<uporime_stran>")
def skupina_change(uporime_stran):
    # Brisanje podatkov
    (uporime_login, ime_login, priimek_login, geslo) = get_user()
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    
    if 'delete' in bottle.request.POST.keys():
        cur.execute('DELETE FROM glasbenik WHERE uporabnisko_ime = %s', (uporime_stran,))
        sporocila.append(("alert-danger", "Izbrisali ste se iz baze."))
    return main(sporocila)


bottle.run(host='localhost', port=8080, debug=True)

conn.commit()
conn.close()

