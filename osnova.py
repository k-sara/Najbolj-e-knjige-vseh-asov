import requests
import csv
import json
import os
import re

podatki = re.compile(
    #id
    r'<div id="(?P<id>\d+)"'
    r'(.|\n)*?'
    #naslov
    r'type="Book">\s*<a title="(?P<naslov>.*)" href='
    r'(.|\n)*?'
    #avtor
    r'<span itemprop="name">(?P<avtor>.*)</span></a>'
    r'(.|\n)*?'
    #povprečje in ocene
    r'span> (?P<povprecje>.*) avg rating &mdash; (?P<ocene>.*) ratings'
    r'(.|\n)*?'
    #Točke:A book’s total score is based on multiple factors,
    #including the number of people who have voted for it
    #and how highly those voters ranked the book
    r'>score: (?P<tocke>.*)<'
    r'(.|\n)*?'
    #število ljudi, ki je glasovalo
    r'>(?P<stevilo_glasujocih>.*) people voted<',
    flags=0 )


#with open('imenik_knjig\\stran-1.html') as f:
#    vsebina = f.read()

#stevilo = 0
#for ujemanje in re.finditer(podatki, vsebina):
#    print(ujemanje.groupdict())
#    stevilo += 1
#print(stevilo)

def shrani_strani(imenik, stevilo_strani=20):
    os.makedirs(imenik, exist_ok=True)
    for stevilka_strani in range(2, stevilo_strani + 1):
        url_strani = (
                'https://www.goodreads.com/list/show/1.Best_Books_Ever?page={}'
            ).format(stevilka_strani)
        stran = requests.get(url_strani)
        ime_datoteke = 'stran-{}.html'.format(stevilka_strani)
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(stran.text)

def preberi_knjige(imenik):
    knjige = []
    for ime_datoteke in os.listdir(imenik):
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, encoding="utf8") as datoteka:
            vsebina = datoteka.read()
            for ujemanje in re.finditer(podatki, vsebina):
                slovar = ujemanje.groupdict()
                knjige.append(slovar)
    return knjige

def zapisi_json(podatki, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        json.dump(podatki, datoteka, indent=2)


def zapisi_csv(podatki, polja, ime_datoteke):
    with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
        pisalec = csv.DictWriter(datoteka, polja, extrasaction='ignore')
        pisalec.writeheader()
        for podatek in podatki:
            pisalec.writerow(podatek)
            
#shrani_strani('imenik_knjig', 20)
seznam_knjig = preberi_knjige('imenik_knjig')
zapis_json = zapisi_json(seznam_knjig, 'najboljse_knjige_vseh_casov.json')
polja = ['id', 'naslov', 'avtor', 'ocene', 'povprecje',
         'stevilo_glasujocih', 'tocke']
zapisi_csv(seznam_knjig, polja, 'najboljse_knjige_vseh_casov.csv')
