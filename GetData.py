import csv
import re

def GetData():
    seznam = []
    print('Pozdravljen. Prosim vnesi svoje podatke. \
Polja označena z * so obvezna. Prosim ne vnašaj bedarij. ')
    str1 = input('Ime: ')
    seznam.append(str1)

    str2 = input('Priimek: ')
    seznam.append(str2)

    str3 = input('*Uporabniško ime: ')
    while str3 == '':
        str3 = input('To polje je obvezno. Prosim, vnesi zahtevano: ')
    seznam.append(str3)

    print('*Spol: ')
    str4 = input('Pritisni 1: Ž \n'
          'Pritisni 2: M \n' )
    while str4 not in ['1', '2']:
        str4 = input('Prosim izberi 1 ali 2. ')
    
    if str4 == '1': seznam.append('Ž')
    else: seznam.append('M')

    str5 = input('*Elektronski naslov: ')
    match_case = r'(.+)@(.+)\.(.*)'
    naslov = re.match(match_case, str5) 
    while naslov == None:
        str5 = input('Prosim vnesi pravilen elektronski naslov: ')
        naslov = re.match(match_case, str5)
    seznam.append(naslov.group())

    str6 = input('*Letnica rojstva: ')
    match_case = r'\d{4}'
    letnica = re.match(match_case, str6)
    print(int(letnica.group()))
    while letnica == None or not (1914 < int(str6) < 2000):
        str6 = input('To sploh ni prava letnica. Prosim vnesi smiselno leto: ')
        letnica = re.match(match_case, str6)
    seznam.append(letnica.group())

    print('*Iščeš skupino?: ')
    str7 = input('Pritisni 1: NE \n'
                 'Pritisni 2: DA \n')
    while str7 not in ['1', '2']:
        str7 = input('Prosim izberi 1 ali 2. ')
    
    if str7 == '1': seznam.append('NE')
    else:
        seznam.append('DA')
        str71 = input('Katere žanre naj igra iskana skupina? Vneseš lahko največ \
5 žanrov. Če ti je vseeno, oziroma ko imaš dovolj, pritisni Enter: \n')
        i = 1
        while str71 != '' and i <= 5:
            i += 1
            seznam.append(str71)
            if i==6: break
            str71 = input('')
        seznam += ['' for k in range(6-i)]
        
    print('To je zaenkrat vse, hvala za tvoje vnose.')
    print(seznam)
