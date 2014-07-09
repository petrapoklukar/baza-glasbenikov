from bottle import *
import sqlite3
import psycopg2, psycopg2.extensions, psycopg2.extras

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


# Static Routes
@get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='static/img')

@get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return static_file(filename, root='static/fonts')

# Ostalo

@route('/')
@get('/')
def main():
    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    CurObcina.execute("SELECT ime FROM obcina ORDER BY ime")
    CurZanr.execute("SELECT ime FROM zanr ORDER BY ime")
    CurStopnja.execute("SELECT stopnja FROM stopnja_znanja")
    CurSpol.execute("SELECT spol FROM spol")
    CurZanr2.execute("SELECT ime FROM zanr ORDER BY ime")
    CurObcina2.execute("SELECT ime FROM obcina ORDER BY ime")
    tmp = template('main.html', uporabnik=cur, obcina=CurObcina, zanr=CurZanr,
                   stopnja=CurStopnja, spol=CurSpol, zanr2=CurZanr2,
                   obcina2=CurObcina2)
    
    
    return tmp

@post('/iskanjeglasbenika')
def iskanje():
    s = """SELECT DISTINCT uporabnisko_ime, ime, priimek, spol, e_mail, glasbilo, stopnja_znanja, 
        leto_zacetka, obcina, igra_zanr, zanr AS isce_skupino_ki_igra FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE glasbilo = %s AND obcina = %s AND igra_zanr = %s
        AND stopnja_znanja = %s AND spol = %s"""
    
    instrument = request.forms.get('instrument')
    if instrument == None: instrument = 'TRUE'
    obcina = request.forms.get('obcina')
    zanr = request.forms.get('zanr')
    stopnja = request.forms.get('stopnja')
    spol = request.forms.get('spol')
    isceskupino = request.forms.get('isceskupino')
    

    CurIskanjeGlasbenika.execute("""SELECT DISTINCT uporabnisko_ime, ime, priimek, spol, e_mail, glasbilo, stopnja_znanja, 
        leto_zacetka, obcina, igra_zanr, zanr AS isce_skupino_ki_igra FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE glasbilo = %s AND obcina = %s AND igra_zanr = %s
        AND stopnja_znanja = %s AND spol = %s """, (instrument, obcina, zanr, stopnja, spol, ))    
    
    return template('iskanjeglasbenika.html', IskanjeGlasbenika = CurIskanjeGlasbenika)

@post('/iskanjeskupine')
def iskanje():
    obcina2 = request.forms.get('obcina2')
    zanr2 = request.forms.get('zanr2')
    isceclane = request.forms.get('isceclane')
    seznam = [('Skupina deluje v okolici občine: ', obcina2), ('Skupina igra žanr: ', zanr2),
              ('Skupina isce clane: ', isceclane)]
    return template('iskanjeskupine.html', seznam=seznam)


@post('/login')
@route('/login')
@route('/login/')
def login():
    return template('login.html')


@post('/noviuporabnik')
@route('/noviuporabnik')
@route('/noviuporabnik/')
def noviuporabnik():
    cur.execute("SELECT ime FROM tip_glasbila_ali_vokal ORDER BY ime")
    CurObcina.execute("SELECT ime FROM obcina ORDER BY ime")
    CurZanr.execute("SELECT ime FROM zanr ORDER BY ime")
    CurStopnja.execute("SELECT stopnja FROM stopnja_znanja")
    CurSpol.execute("SELECT spol FROM spol")
    
    return template('signin.html', uporabnik=cur, obcina=CurObcina, zanr=CurZanr,
                   stopnja=CurStopnja, spol=CurSpol)
    


@post('/uporabnik')
@route('/uporabnik')
@route('/uporabnik/')
def uporabnik():
    uporime = request.forms.get('uporime')
    geslo = request.forms.get('geslo')
    CurTabelaInstrumentov.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime,))
    CurUporabnik.execute("""SELECT DISTINCT ime, priimek, e_mail, leto_rojstva, uporabnisko_ime, spol, obcina, igra_zanr, zanr FROM glasbenik
        JOIN igra_poje ON igra_poje.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_deluje_v_okolici ON glasbenik_deluje_v_okolici.glasbenik = glasbenik.uporabnisko_ime
        JOIN glasbenik_igra_zanr ON glasbenik_igra_zanr.glasbenik = glasbenik.uporabnisko_ime
        LEFT JOIN glasbenik_isce_skupino ON glasbenik_isce_skupino.glasbenik = glasbenik.uporabnisko_ime
        WHERE uporabnisko_ime = %s""", (uporime,))
    #print(CurUporabnik.fetchall())
    return template('uporabnik.html', uporime=uporime, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=CurUporabnik)


@post('/signin')
@route('/signin')
@route('/signin/')
def signin():
    krof = False
    instrument = request.forms.get('instrument')
    obcina = request.forms.get('obcina')
    zanr = request.forms.get('zanr')
    stopnja = request.forms.get('stopnja')
    spol = request.forms.get('spol')
    isceskupino = request.forms.get('isceskupino')
    ime1 = request.forms.get('ime1')
    priimek1 = request.forms.get('priimek1')
    mail1 = request.forms.get('mail1')
    letorojstva = request.forms.get('letorojstva')
    uporime = request.forms.get('username1')
    geslo1 = request.forms.get('geslo1')
    geslo2 = request.forms.get('geslo2')

    Uporabnik = [[ime1, priimek1, mail1, letorojstva, uporime, spol, obcina, zanr, isceskupino]]
    CurTabelaInstrumentov.execute("SELECT glasbilo, stopnja_znanja, leto_zacetka FROM igra_poje WHERE glasbenik = %s ", (uporime,))

    return template('uporabnik.html', uporime=uporime, TabelaInstrumentov=CurTabelaInstrumentov, Uporabnik=Uporabnik)

    
##    geslo1 = request.forms.get('geslo1')
##    geslo2 = request.forms.get('geslo2')
##    ime = request.forms.get('ime')
##    priimek = request.forms.get('priimek')
##    mail = request.forms.get('mail')
##    letnica = request.forms.get('letnica')
    
    
    

run(host='localhost', port=8080, debug=True)

conn.commit()
conn.close()

