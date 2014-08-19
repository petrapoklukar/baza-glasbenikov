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
CurObcina = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurZanr = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurStopnja = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurSpol = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurZanr2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurObcina2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurTabelaInstrumentov = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurUporabnik = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurIskanjeGlasbenika = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

CurRegistracija1=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurRegistracija2=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurRegistracija3=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurRegistracija4=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
CurRegistracija5=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

CurVpis=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

CurPrijavljen=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        CurPrijavljen.execute("SELECT uporabnisko_ime, ime, priimek FROM glasbenik WHERE uporabnisko_ime=%s",
                  (username,))
        r = CurPrijavljen.fetchone()
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
    CurObcina.execute("SELECT ime FROM obcina ORDER BY ime")
    CurZanr.execute("SELECT ime FROM zanr ORDER BY ime")
    CurStopnja.execute("SELECT stopnja FROM stopnja_znanja")
    CurSpol.execute("SELECT spol FROM spol")
    CurZanr2.execute("SELECT ime FROM zanr ORDER BY ime")
    CurObcina2.execute("SELECT ime FROM obcina ORDER BY ime")
    tmp = bottle.template('main.html', uporabnik=cur, obcina=CurObcina, zanr=CurZanr,
                   stopnja=CurStopnja, spol=CurSpol, zanr2=CurZanr2,
                   obcina2=CurObcina2)
    
    
    return tmp



@bottle.post('/iskanjeglasbenika')
def iskanje():
    s = """SELECT DISTINCT uporabnisko_ime, ime, priimek, spol, e_mail, glasbilo, stopnja_znanja, 
        leto_zacetka, obcina, igra_zanr, zanr AS isce_skupino_ki_igra FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE glasbilo = %s AND obcina = %s AND igra_zanr = %s
        AND stopnja_znanja = %s AND spol = %s"""
    
    instrument = bottle.request.forms.getunicode('instrument')
    if instrument == None: instrument = 'TRUE'
    obcina = bottle.request.forms.getunicode('obcina')
    zanr = bottle.request.forms.getunicode('zanr')
    stopnja = bottle.request.forms.getunicode('stopnja')
    spol = bottle.request.forms.getunicode('spol')
    isceskupino = bottle.request.forms.getunicode('isceskupino')

    
    CurIskanjeGlasbenika.execute("""SELECT DISTINCT uporabnisko_ime, ime, priimek, spol, e_mail, glasbilo, stopnja_znanja, 
        leto_zacetka, obcina, igra_zanr, zanr AS isce_skupino_ki_igra FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE glasbilo = %s AND obcina = %s AND igra_zanr = %s
        AND stopnja_znanja = %s AND spol = %s """, (instrument, obcina, zanr, stopnja, spol, ))    
    
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
    
    CurVpis.execute("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s AND geslo=%s",
              (username, password))
    if CurVpis.fetchone() is None:
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
    CurObcina.execute("SELECT ime FROM obcina ORDER BY ime")
    CurZanr.execute("SELECT ime FROM zanr ORDER BY ime")
    CurStopnja.execute("SELECT stopnja FROM stopnja_znanja")
    CurSpol.execute("SELECT spol FROM spol")
    
    return bottle.template('signin.html', glasbilo=cur, obcina=CurObcina, zanr=CurZanr,
                           stopnja=CurStopnja, spol=CurSpol, napaka='alarm!', uporime=None,
                           ime1=None, priimek1=None, mail1=None, letorojstva=None)
    
"""
@post('/login')
@route('/login')
@route('/login/')
def login():
    return template('login.html')
"""



@bottle.post('/uporabnik')
@bottle.route('/uporabnik')
@bottle.route('/uporabnik/')
def uporabnik():
    # Kdo je prijavljeni uporabnik? 
    (uporime_login, ime_login, priimek_login) = get_user()
    #uporime = bottle.request.forms.get('uporime')
    #geslo = bottle.request.forms.get('geslo')
    
    CurTabelaInstrumentov.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime_login,))
    CurUporabnik.execute("""SELECT DISTINCT ime, priimek, e_mail, leto_rojstva, uporabnisko_ime, spol, obcina, igra_zanr, zanr FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE uporabnisko_ime = %s""", (uporime_login,))
    #return print(type(CurUporabnik.fetchall()))
    return bottle.template('uporabnik.html', uporime=uporime_login, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=CurUporabnik)



@bottle.post('/signin')
@bottle.route('/signin')
@bottle.route('/signin/')
def signin():
    krof = False
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
    CurObcina.execute("SELECT ime FROM obcina ORDER BY ime")
    CurZanr.execute("SELECT ime FROM zanr ORDER BY ime")
    CurStopnja.execute("SELECT stopnja FROM stopnja_znanja")
    CurSpol.execute("SELECT spol FROM spol")
    
    Uporabnik = [[ime1, priimek1, mail1, letorojstva, uporime, spol, obcina, zanr, isceskupino]]
    CurTabelaInstrumentov.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime,))
    
    # Ali uporabnik že obstaja?
    CurRegistracija1.execute("SELECT 1 FROM glasbenik WHERE uporabnisko_ime=%s", (uporime,))
    if CurRegistracija1.fetchone():
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
        
        CurRegistracija2.execute("""INSERT INTO glasbenik (uporabnisko_ime, ime, priimek, spol, e_mail, leto_rojstva, geslo)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",(uporime, ime1, priimek1, spol, mail1, letorojstva, password_md5(geslo1)))

        CurRegistracija3.execute("""INSERT INTO igra_poje (glasbenik, glasbilo, stopnja_znanja, leto_zacetka)
                                VALUES (%s, %s, %s, %s)""", (uporime, instrument, stopnja, None))

        CurRegistracija4.execute("""INSERT INTO glasbenik_igra_zanr (glasbenik, igra_zanr)
                                VALUES (%s, %s)""", (uporime, zanr))

        # kaj je z žanrom pri iskanju skupine?
        #CurRegistracija.execute("""INSERT INTO glasbenik_isce_skupino (glasbenik, zanr)
                                #VALUES (%s, %s)""", (uporime, zanr))

        CurRegistracija5.execute("""INSERT INTO glasbenik_deluje_v_okolici (glasbenik, obcina)
                                VALUES (%s, %s)""", (uporime, obcina))
        
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', uporime, path='/', secret=secret)
        bottle.redirect("/uporabnik") #to je uporabil bauer-redirect
    
    #return bottle.template('uporabnik.html', uporime=uporime, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=Uporabnik)



    
##    geslo1 = request.forms.get('geslo1')
##    geslo2 = request.forms.get('geslo2')
##    ime = request.forms.get('ime')
##    priimek = request.forms.get('priimek')
##    mail = request.forms.get('mail')
##    letnica = request.forms.get('letnica')
    
    
    

bottle.run(host='localhost', port=8080, debug=True)

conn.commit()
conn.close()

