# -*- coding: <utf-8> -*-
import bottle
import sqlite3
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib # računanje MD5 kriptografski hash za gesla


# KONFIGURACIJA
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database='seminarska_matjazz', host='audrey.fmf.uni-lj.si', user='matjazz', password='marmelada')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


# Static Routes
@bottle.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root='static/js')

@bottle.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return bottle.static_file(filename, root='static/css')

@bottle.get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root='static/img')

@bottle.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename, root='static/fonts')

# Ostalo

# Bauerjevi cookiji :) (copy-paste)
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
        #CurPrijavljen=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT uporabnisko_ime, ime, priimek FROM glasbenik WHERE uporabnisko_ime=%s",
                  (username,))
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    if auto_login:
        bottle.redirect('/')
    else:
        return None



@bottle.route('/')
@bottle.get('/')
def main():
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
    
    tmp = bottle.template('main.html', uporabnik=uporabnik, obcina=CurObcina, zanr=CurZanr,
                   stopnja=CurStopnja, spol=CurSpol, zanr2=CurZanr2,
                   obcina2=CurObcina2, isce = CurIsce)
    return tmp


@bottle.post('/iskanjeglasbenika')
def iskanje(): 
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
    
    return bottle.template('iskanjeglasbenika.html', IskanjeGlasbenika = CurIskanjeGlasbenika)


@bottle.post('/iskanjeskupine')
def iskanje():
    obcina2 = bottle.request.forms.get('obcina2')
    zanr2 = bottle.request.forms.get('zanr2')
    #isceclane = bottle.AutoServerrequest.forms.get('isceclane')
    isceclane = bottle.request.forms.get('isceclane')
    seznam = [('Skupina deluje v okolici občine: ', obcina2), ('Skupina igra žanr: ', zanr2),
              ('Skupina isce clane: ', isceclane)]
    return bottle.template('iskanjeskupine.html', seznam=seznam)


@bottle.get('/login')
#@bottle.post('/login')
@bottle.route('/login')
@bottle.route('/login/')
def login_get():
    """Serviraj formo za login."""
    return bottle.template('login.html',napaka=None,uporime=None)

@bottle.get("/logout/") # naslov na katerem ti pobriše kuki in te vrže na glavno stran
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('username')
    bottle.redirect('/')


@bottle.post("/login")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.getunicode('uporime')
   
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.getunicode('geslo'))
    # Preverimo, ali se je uporabnik pravilno prijavil
    
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
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/uporabnik") 


@bottle.post('/noviuporabnik')
@bottle.route('/noviuporabnik')
@bottle.route('/noviuporabnik/')
# registracija-get
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
    
    return bottle.template('signin.html', glasbilo=glasbilo, obcina=CurObcina, zanr=CurZanr,
                           stopnja=CurStopnja, spol=CurSpol, napaka=None, uporime=None,
                           ime1=None, priimek1=None, mail1=None, letorojstva=None)


@bottle.post('/uporabnik')
@bottle.route('/uporabnik')
@bottle.route('/uporabnik/')
def uporabnik():
    # Kdo je prijavljeni uporabnik? 
    (uporime_login, ime_login, priimek_login) = get_user()
    #uporime = bottle.request.forms.get('uporime')
    #geslo = bottle.request.forms.get('geslo')
    
    cur.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime_login,))
    CurTabelaInstrumentov = cur.fetchall()
    
    cur.execute("""SELECT DISTINCT ime, priimek, e_mail, leto_rojstva, uporabnisko_ime, spol, obcina, igra_zanr, zanr FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE uporabnisko_ime = %s""", (uporime_login,))
    CurUporabnik = cur.fetchall()

    # TA SELECT NE DELUJE ZA UPORABNIKA_1 !!!!!!
    #print(CurUporabnik)
    
    #return print(type(CurUporabnik.fetchall()))
    return bottle.template('uporabnik.html', uporime=uporime_login, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=CurUporabnik)


@bottle.post('/signin')
@bottle.route('/signin')
@bottle.route('/signin/')
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
        return bottle.template('signin.html', glasbilo=cur, obcina=CurObcina, zanr=CurZanr,
                               stopnja=CurStopnja, spol=CurSpol, napaka='To uporabniško ime je že zavzeto!',
                               ime1=ime1, priimek1=priimek1, mail1=mail1, letorojstva=letorojstva,uporime=None)
    elif not geslo1 == geslo2:
        # Geslo se ne ujemata
        return bottle.template('signin.html', glasbilo=cur, obcina=CurObcina, zanr=CurZanr,
                               stopnja=CurStopnja, spol=CurSpol, napaka='Gesli se ne ujemata!',
                               uporime=uporime, ime1=ime1, priimek1=priimek1, mail1=mail1,
                               letorojstva=letorojstva)
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        #password = password_md5(password1)
        
        cur.execute("""INSERT INTO glasbenik (uporabnisko_ime, ime, priimek, spol, e_mail, leto_rojstva, geslo)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",(uporime, ime1, priimek1, spol, mail1, letorojstva, password_md5(geslo1)))
        CurRegistracija2 = cur.fetchall()

        cur.execute("""INSERT INTO igra_poje (glasbenik, glasbilo, stopnja_znanja, leto_zacetka)
                                VALUES (%s, %s, %s, %s)""", (uporime, instrument, stopnja, None))
        CurRegistracija3 = cur.fetchall()

        cur.execute("""INSERT INTO glasbenik_igra_zanr (glasbenik, igra_zanr)
                                VALUES (%s, %s)""", (uporime, zanr))
        CurRegistracija4 = cur.fetchall()

        # kaj je z žanrom pri iskanju skupine?
        #CurRegistracija.execute("""INSERT INTO glasbenik_isce_skupino (glasbenik, zanr)
                                #VALUES (%s, %s)""", (uporime, zanr))

        cur.execute("""INSERT INTO glasbenik_deluje_v_okolici (glasbenik, obcina)
                                VALUES (%s, %s)""", (uporime, obcina))
        CurRegistracija5 = cur.fetchall()
        
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', uporime, path='/', secret=secret)
        bottle.redirect("/uporabnik") #to je uporabil bauer-redirect
    
    #return bottle.template('uporabnik.html', uporime=uporime, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=Uporabnik)


bottle.run(host='localhost', port=8080, debug=True)

conn.commit()
conn.close()

