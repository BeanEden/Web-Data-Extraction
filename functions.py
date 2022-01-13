import requests
from bs4 import BeautifulSoup as bs
import concurrent.futures
import time
import requests
from bs4 import BeautifulSoup as bs
import csv
import shutil
import os
import genericpath
from functions import *

url_index = "http://books.toscrape.com/index.html"

EN_TETE_COLONNES = (
    "product_page_url",
    "universal_product_code (upc)",
    "title",
    "price_excluding_tax",
    "price_including_tax",
    "number available",
    "product_description",
    "category",
    "review_rating",
    "image_url"
)

def soup_function(url_soup):
    """Automatisation du parsage html
    on peut gagner une ligne, au détriment de la lisibilité en skippant la variable "page" > soup = (reponse.content.decode('utf-8'), "html.parser")"""
    reponse = requests.get(url_soup)
    page = reponse.content
    soup = bs(page.decode('utf-8'), "html.parser")
    return(soup)


def extraction_tableau(soup):
    """Extraction de l'upc, des prix (avec et sans taxes), et des stocks
    Argument : soup
    Retourne une liste"""
    liste_informations = list(map(lambda x: x.string, soup.find_all("td", )))
    del liste_informations[-1]
    del liste_informations[4]
    del liste_informations[1]

    return liste_informations


def extraction_description(soup):
    """Extraction de la description (en liste pour uniformisation de l'encodage)"""
    description_val = list(map(lambda x: x.string, soup.find_all("p", class_=None)))
    # description_val = description_val[0]
    return description_val


def extraction_categorie(soup):
    """Extraction de la catégorie"""
    categorie_string = ""
    liste_ariane = []
    boxCategory = soup.find('ul', class_="breadcrumb")
    liste = tuple(liste_noms_categories())
    liste_ariane = list(map(lambda x : x.string, boxCategory("a", href_="")))
    categorie_string = list(x for x in liste_ariane if x in liste)
    categorie_string = categorie_string[0]
    return categorie_string


def extraction_rating(soup):
    """Extraction de la notation
    Comparatif avec une liste et retour d'une valeur définie"""

    ratings = ("One", "Two", "Three", "Four", "Five")
    box_rating = soup.find('div', class_="col-sm-6 product_main")
    review_rating_string = list(x for x in ratings if box_rating.find('p', class_=x) is not None)
    review_rating_string = review_rating_string[0]
    return review_rating_string


def extraction_titre(soup):
    """Extraction du titre
    Argument : soup
    Retourne une string"""
    titre_livre_string = soup.h1.string
    return titre_livre_string


def extraction_url_image(soup):
    # Extraction et insertion de l'url de l'image
    box_image = soup.find("div", class_="item active")
    url_image_string = list(map(lambda x: x.get("src").replace("../../", "http://books.toscrape.com/"), box_image.find_all("img")))
    url_image_string = url_image_string[0]
    return url_image_string


def construction_titre_image(liste):
    liste_nom = liste[2]
    elements_encodage = [":","/",'\'','"','*',"?","!","’"]
    titre_image = str(liste_nom[0:25]) + '.jpg'
    titre_image = titre_image.replace(":","")
    titre_image = titre_image.replace("/","")
    titre_image = titre_image.replace('\'',"")
    titre_image = titre_image.replace('"',"")
    titre_image = titre_image.replace('*', "")
    titre_image = titre_image.replace("?","")
    titre_image = titre_image.replace("!","")
    titre_image = titre_image.replace("’","")
    # titre_image = map(lambda x: titre_image.strip(x) + '.jpg', elements_encodage))

    return titre_image


def liste_url_categories():
    """Création de la liste des url de catégorie
    Cette fonction ne requiert aucun argument et génère la liste suivante [urlcategorie1, urlcategorie2,...]
    Elle se base sur la page d'accueil du site, extrait les url et les corrige (ajoute http://books.toscrape.com au début des url)"""
    complet_url = "http://books.toscrape.com/"
    soup = soup_function(url_index)

    box_livres = soup.find('ul', class_='nav')
    url_categories = list(map(lambda x : (complet_url + x['href']), box_livres.find_all('a', href=True)))
    del url_categories[0]

    return(url_categories)


def liste_noms_categories():
    soup = soup_function(url_index)
    box_noms = soup.find('ul', class_='nav')

    titre_categories = list(map(lambda x: x.get_text().strip('\n                            \n                        '),box_noms.find_all('a', href=True)))
    del titre_categories[0]

    return titre_categories


def liste_url_livres_categorie(url_categorie):
    """Extrait les url de tous les livres présent sur UNE page catégorie
    Argument : URL d'une page de catégorie (pas de différence page 1 ou page 2)
    Retourne une liste"""

    root = "http://books.toscrape.com/catalogue/"
    soup = soup_function(url_categorie)

    box_livres = soup.find('ol', class_='row')
    liste_categorie_intermediaire = []
    # liste_categorie_intermediaire = list(map(lambda x: x['href'], box_livres.find_all('a', href=True)))
    for a in box_livres.find_all('a', href=True):
        liste_categorie_intermediaire.append(a['href'])
    liste_url_livres_categorie = list(dict.fromkeys(liste_categorie_intermediaire))
    liste_finale_url_livres = list(map(lambda x: x.replace("../../../", root),liste_url_livres_categorie))

    return liste_finale_url_livres


def verification_page_2(urlPage):
    """Verifie l'existence d'une seconde page dans la categorie"""
    soup = soup_function(urlPage)

    box_page = soup.find('li', class_='next')
    page_index = ""
    if box_page is not None :
        # page_index = str(map(lambda x: x['href'], box_page.find_all('a', href=True)))
        for a in box_page.find_all('a', href=True):
            page_index = (a['href'])
    else :
        page_index = None
    return(page_index)


def liste_tous_livres_categorie(url_page_index_categorie):
    """Recupère l'ensemble des url des livres de la categorie (sur toutes les pages)"""
    liste_toutes_pages = liste_url_livres_categorie(url_page_index_categorie)
    page_n = verification_page_2(url_page_index_categorie)

    if url_page_index_categorie.find("page-1") >= -1 :
        url_page_index_categorie = url_page_index_categorie.replace("page-1.html","index.html")

    while page_n is not None:        # boucle selon la pagination (tant qu'il existe une page suivante, on continue)
        url_new_page = url_page_index_categorie.replace("index.html", page_n)
        page_n = verification_page_2(url_new_page)
        liste_toutes_pages.extend(liste_url_livres_categorie(url_new_page))

    return liste_toutes_pages


def nom_categorie(url_categorie):
    # categorieListe = []
    # for titre in categorieFinder():
    soup = soup_function(url_categorie)
    nom_categorie = (soup.h1.string)
    return nom_categorie


def creation_un_livre(url_page_livre):
    soup = soup_function(url_page_livre)

    liste_informations_livre = []
    liste_informations_livre.append(url_page_livre)
    liste_informations_livre.extend(extraction_tableau(soup))
    liste_informations_livre.insert(2,extraction_titre(soup))
    liste_informations_livre.extend(extraction_description(soup))
    liste_informations_livre.append(extraction_categorie(soup))
    liste_informations_livre.append(extraction_rating(soup))
    liste_informations_livre.append(extraction_url_image(soup))

    return liste_informations_livre


def thread_creation(liste):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tables = list(executor.map(lambda x : creation_un_livre(x), liste))
    return tables







def chemin_acces():
    cwd = os.getcwd()
    cwd_data = cwd + "/data/"
    return cwd_data


def creation_dossier_data(cwd_data):
    """Création d'un dossier data si non existant"""
    if genericpath.isdir(cwd_data) is not True:
        os.mkdir(cwd_data)
        print("Dossier data créé")


def creation_dossier_categorie(cwd_data, categories):
    """Création d'un dossier par categorie si non existant"""
    nom_dossier_categorie = nom_categorie(categories)
    directory = cwd_data + nom_dossier_categorie + '/'
    if genericpath.isdir(directory) is not True:
        os.mkdir(directory)
        print("Dossier " + nom_dossier_categorie + ' créé')
    else:
        print("Dossier " + nom_dossier_categorie + " déjà existant")
#
    # start = int(time.time())
# def creation_csv(cwd_data, nom_dossier_categorie):
    nom_csv = nom_dossier_categorie + '.csv'
    directory = cwd_data + nom_dossier_categorie + '/'
    with open(os.path.join(directory + nom_csv), 'w', newline="", encoding="utf-8-sig") as csv_file:
        ligneXcel = csv.writer(csv_file, delimiter=',')
        ligneXcel.writerow(EN_TETE_COLONNES)
        for livres in liste_tous_livres_categorie(categories):
            informations = creation_un_livre(livres)
            ligneXcel.writerow(creation_un_livre(livres))
            telechargement_images(directory, informations)
    # end = int(time.time())
    print(nom_dossier_categorie + ' terminé')
    # print(str(end - start) + ' secondes écoulées')


def telechargement_images(directory, liste):
    with open(os.path.join(directory + construction_titre_image(liste)),'wb') as f:
        r = requests.get(liste[-1], stream=True)
        shutil.copyfileobj(r.raw, f)

