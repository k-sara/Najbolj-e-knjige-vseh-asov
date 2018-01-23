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

referenca = re.compile(
    r'<a class="bookTitle" itemprop="url" href="(.*)">',
    flags=0 )

jez = re.compile(
    #jezik
    r'''Edition Language</div>\s*<div class="infoBoxRowItem" itemprop='inLanguage'>(?P<jezik>.*)</div>''',
    flags=0 )

leto_obj = re.compile(
    #leto objave glasovane izdaje/verzije knjige
    r'<div class="row">\s*Published\s*.*(?P<leto_objave>\d{4})\s*by',
    flags=0 )

leto_izd = re.compile(
    #leto prve izdaje knjige 
    r'first published (?P<leto_izdaje>\d{4})',
    flags=0 )

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

def preberi_reference(imenik):
    reference = []
    for ime_datoteke in os.listdir(imenik):
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, encoding="utf8") as datoteka:
            vsebina = datoteka.read()
            for ujemanje in re.finditer(referenca, vsebina):
                slovar = ujemanje.group(1)
                reference.append(slovar)
    return reference

def shrani_stran_knjige(imenik, seznam):
    os.makedirs(imenik, exist_ok=True)
    for referenca in seznam:
        url_strani = (
                'https://www.goodreads.com{}'
            ).format(referenca)
        stran = requests.get(url_strani)
        ime_datoteke = '{}.html'.format(seznam.index(referenca))
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(stran.text)

def preberi(imenik):
    novi_seznam = []
    for n in range(2000):
        ime_datoteke = '{}.html'.format(n)
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, encoding="utf8") as datoteka:
            vsebina = datoteka.read()
            
            jezik = re.findall(jez, vsebina)
            if jezik == []:
                jezik = None
            else:
                jezik = jezik[0]
            
            leto_objave = re.findall(leto_obj, vsebina)
            if leto_objave == []:
                leto_objave = None
            else:
                leto_objave = int(leto_objave[0])
                
            leto_izdaje = re.findall(leto_izd, vsebina)
            if leto_izdaje == []:
                leto_izdaje = None
            else:
                leto_izdaje = int(leto_izdaje[0])
                
            novi_slovar = {'jezik' :  jezik,
                          'leto_objave' : leto_objave,
                          'leto_izdaje' : leto_izdaje}
            novi_seznam.append(novi_slovar) 
    return novi_seznam

def dopolni_slovar(stari_sez, novi_sez):
    for knjiga in stari_sez:
        mesto = stari_sez.index(knjiga)
        dodatek = novi_sez[mesto]
        knjiga.update(dodatek)
    return stari_sez

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
            
#seznam_ref = preberi_reference('imenik_knjig')
#shrani_stran_knjige('imenik_posameznih_knjig', seznam_ref)

novi_seznam = preberi('imenik_posameznih_knjig')

dopolnjeni_slovar = dopolni_slovar(seznam_knjig, novi_seznam)
            
#zapis_json = zapisi_json(seznam_knjig, 'najboljse_knjige_vseh_casov.json')
#zapis_json2 = zapisi_json(dopolnjeni_slovar, 'najboljse_knjige_vseh_casov2.json')

polja = ['id', 'naslov', 'avtor',
         'ocene', 'povprecje',
         'stevilo_glasujocih',
         'tocke', 'jezik', 'leto_objave',
         'leto_izdaje']
zapisi_csv(dopolnjeni_slovar, polja, 'najboljse_knjige_vseh_casov.csv')
