# uvoz s pomočjo xlrd

import hashlib # računanje MD5 kriptografski hash za gesla
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database='seminarska_roki', host='audrey.fmf.uni-lj.si', user='roki', password='stargate')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


import xlrd # knjižnica za branje excelovih dokumnetov
# odpremo excel file z uporabo knjiznice xlrd
workbook = xlrd.open_workbook('Podatki_za_v_bazo.xlsx')
# iz njega dobimo objekt, ki predstavlja prvi sheet


# NAJPREJ FIKSNE TABELE

# ------------------------------------------------------------------

# OBCINA

sheet = workbook.sheet_by_index(4)

for y in range(1,210):
        row=[]
        for x in range(1):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
                # vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
                # ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                
                # else: vredenost=vrednost.encode('utf8')
                # print("stolpec: %d, vrstica: %d, vsebina: %s\n" % (x, y, vrednost)#encode('utf8')))
                row.append(vrednost)
        #print(row)
	
        cur.execute("""INSERT INTO obcina (ime) VALUES (%s)""", (row[0],))


# SPOL

sheet = workbook.sheet_by_index(5) 

for y in range(1,3):
        row=[]
        for x in range(1):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO spol (spol)
        VALUES (%s)""",(row[0],))


# STOPNJA ZNANJA

sheet = workbook.sheet_by_index(6) 

for y in range(1,4):
        row=[]
        for x in range(1):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute(""" INSERT INTO stopnja_znanja (stopnja)
        VALUES (%s)""",(row[0],))

# ZANR

sheet = workbook.sheet_by_index(12)

for y in range(1,856):
        row=[]
        for x in range(1):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
                # vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
                # ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                
                # else: vredenost=vrednost.encode('utf8')
                # print("stolpec: %d, vrstica: %d, vsebina: %s\n" % (x, y, vrednost)#encode('utf8')))
                row.append(vrednost)
        #print(row)
	
        cur.execute("""INSERT INTO zanr (ime) VALUES (%s)""", (row[0],))



# TIP GLASBILA ALI VOKAL

sheet = workbook.sheet_by_index(7) 

for y in range(1,70):
        row=[]
        for x in range(1):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO tip_glasbila_ali_vokal (ime) VALUES (%s)""",(row[0],))



#---------------  manj pomembni -----------------------------------------------------------

# KONCERTNO PRIZORIŠČE
sheet = workbook.sheet_by_index(3) 

for y in range(1,21):
        id_number=y
        row=[]
        for x in range(5):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
                # vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
                # ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                
                # else: vredenost=vrednost.encode('utf8')
                # print("stolpec: %d, vrstica: %d, vsebina: %s\n" % (x, y, vrednost)#encode('utf8')))
                row.append(vrednost)
        #print(row)
                
        cur.execute("""INSERT INTO koncertno_prizorisce (id, e_mail, telefonska_stevilka, ime, se_nahaja_v)
        VALUES (%s, %s, %s, %s, %s)""",
        (id_number, row[1], int(row[2]), row[3], row[4]))



# EVENTI

sheet = workbook.sheet_by_index(2) 

for y in range(1,21):
        id_number=y
        row=[]
        for x in range(3):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                if x==0: vrednost=xlrd.xldate_as_tuple(vrednost,0)
                row.append(vrednost)
        #print(row)
        date='%.i-%.i-%.i'%(row[0][0],row[0][1],row[0][2])
        cur.execute("""INSERT INTO event (datum, ime, prizorisce) VALUES (%s, %s, %s)""",(date, row[1], id_number))

# pazimo na datume. Excel jih zakodira kot float



# MODEL (to bi blo treb popravit)

"""
sheet = workbook.sheet_by_index(14) 

for y in range(1,59):
        row=[]
        for x in range(4):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""#INSERT INTO model (ime_modela, lastnik, vrsta_glasbila, za_izposojo)
        #VALUES (%s,%s,%s,%s)""",(row[2],row[0],row[1],1==row[3]))
"""
"""
#---------------------------------------------------------------------------------------------

# GLASBENIK
sheet = workbook.sheet_by_index(1) 

for y in range(1,101):
        row=[]
        for x in range(6):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
                # vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
                # ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                
                # else: vredenost=vrednost.encode('utf8')
                # print("stolpec: %d, vrstica: %d, vsebina: %s\n" % (x, y, vrednost)#encode('utf8')))
                row.append(vrednost)
        #print(row)
                
        cur.execute("""INSERT INTO glasbenik (uporabnisko_ime, ime, priimek, spol, e_mail, leto_rojstva, geslo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (row[0], row[1], row[2], row[3], row[4], int(row[5]), password_md5(row[0])))


# GLASBENIK IGRA ŽANR

sheet = workbook.sheet_by_index(20)

for y in range(1,101):
        row=[]
        for x in range(2):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO glasbenik_igra_zanr (glasbenik, igra_zanr)
        VALUES (%s,%s)""",(row[0],row[1]))




# SKUPINA

sheet = workbook.sheet_by_index(8) 

for y in range(1,21):
        row=[]
        for x in range(6):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                if x==1: vrednost=xlrd.xldate_as_tuple(vrednost,0)
                row.append(vrednost)
        date='%.i-%.i-%.i'%(row[1][0],row[1][1],row[1][2])
        #print(row)
        cur.execute("""INSERT INTO skupina (ime,datum_ustanovitve,e_mail,spletna_stran,fb,telefonska_stevilka)
        VALUES (%s,%s,%s,%s,%s,%s)""",(row[0],date,row[2],row[3],row[4],int(row[5])))

# CLANI SKUPINE

sheet = workbook.sheet_by_index(9) 

for y in range(1,75):
        row=[]
        for x in range(3):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO clani_skupine (skupina, clan, glasbilo)
        VALUES (%s,%s,%s)""",(row[0],row[1],row[2]))


# GLASBENIK DELUJE V OKOLICI

sheet = workbook.sheet_by_index(10) 

for y in range(1,150):
        row=[]
        for x in range(2):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO glasbenik_deluje_v_okolici (glasbenik, obcina)
        VALUES (%s,%s)""",(row[0],row[1]))



# GLASBENIK ISCE SKUPINO

sheet = workbook.sheet_by_index(11) 

for y in range(1,88):
        row=[]
        for x in range(2):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO glasbenik_isce_skupino (glasbenik, zanr)
        VALUES (%s,%s)""",(row[0],row[1]))



# IGRA POJE

sheet = workbook.sheet_by_index(13) 

for y in range(1,100):
        row=[]
        for x in range(4):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO igra_poje (glasbenik, glasbilo, stopnja_znanja, leto_zacetka)
        VALUES (%s,%s,%s,%s)""",(row[0],row[1],row[2],int(row[3])))



# SKUPINA DELUJE V OKOLICI

sheet = workbook.sheet_by_index(16) 

for y in range(1,34):
        row=[]
        for x in range(2):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO skupina_deluje_v_okolici (skupina, obcina)
        VALUES (%s,%s)""",(row[0],row[1]))



# SKUPINA IGRA ZANR

sheet = workbook.sheet_by_index(17) 

for y in range(1,36):
        row=[]
        for x in range(2):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO skupina_igra_zanr (skupina, igra_zanr)
        VALUES (%s,%s)""",(row[0],row[1]))


# SKUPINA ISCE

sheet = workbook.sheet_by_index(18) # tuba moški in tuba ženska - podvajanje ključa!

for y in range(1,19):
        row=[]
        for x in range(4):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                row.append(vrednost)
        #print(row)
        cur.execute("""INSERT INTO skupina_isce (skupina, glasbilo,spol,stevilo)
        VALUES (%s,%s,%s,%s)""",(row[0],row[1],row[2],int(row[3])))



# SKUPINA JE IGRALA

sheet = workbook.sheet_by_index(19) 

for y in range(1,21):
        row=[]
        for x in range(3):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
		# vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
		# ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                if x==1: vrednost=xlrd.xldate_as_tuple(vrednost,0)
                row.append(vrednost)
        #print(row)
        date='%.i-%.i-%.i'%(row[1][0],row[1][1],row[1][2])
        cur.execute("""INSERT INTO skupina_je_igrala (skupina, event_datum, event_ime)
        VALUES (%s,%s,%s)""",(row[0],date,row[2]))



# VADNICE

sheet = workbook.sheet_by_index(21)

for y in range(1,17):
        row=[]
        for x in range(5):
                # najdemo vrednost celice s koordinatami (x,y)
                vrednost = sheet.cell(y, x).value # najprej vrstica, nato stolpec!!!
                # vrednost zakodiramo v UTF8 (to je potrebno samo za izpisovanje;
                # ce bi vrednost potlacili v bazo, ne bi nic zakodirali) in izpisemo
                
                # else: vredenost=vrednost.encode('utf8')
                # print("stolpec: %d, vrstica: %d, vsebina: %s\n" % (x, y, vrednost)#encode('utf8')))
                row.append(vrednost)
        #print(row)
	
        cur.execute("""INSERT INTO vadnica (id, e_mail, telefonska_stevilka, ime, se_nahaja_v)
        VALUES (%s, %s, %s, %s, %s)""", (int(row[0]), row[1], int(row[2]), row[3], row[4]))





conn.commit()

cur.close()
conn.close()

