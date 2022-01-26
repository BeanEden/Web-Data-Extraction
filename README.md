#README Project 2 OpenClassrooms
#Utilisez les bases de Python pour l'analyse de marché
par Jean-Corentin Loirat
le 07/12/2021 (mis à jour le 13/01/2022)

Lien du repository git hub :
<a href=https://github.com/BeanEden/OcrProjet2.git></a>




##Description :
Il s'agit d'un script permettant d'extraire du site : <a href=http://books.toscrape.com/index.html></a> des informations et images concernant des livres.
Le script récupère, pour chaque livre présent sur le site, les informations suivantes :
 * product_page_url
 * universal_ product_code (upc)
 * title
 * price_including_tax
 * price_excluding_tax
 * number_available
 * product_description
 * category
 * review_rating
 * image_url 
Ces informations sont extraites catégorie par catégorie (exemple : Travel, Mystery...) et écrites dans un fichier csv par catégorie.
Les images des livres sont également récupérées.

L'ensemble de ces données est intégré dans un nouveau dossier "data".
Chaque catégorie dispose ensuite de son propre dossier (exemple : le dossier ../data/Travel contient le Csv et les images de la catégorie Travel).


## Utilisation :
### 1 - Créez un environement virtuel dans le dossier de votre choix :
$ mkdir projects
$ cd projects
$ ls
~/project

### 2 - Importez les packages :
#### Commande terminal : pip install -r requirements.txt
Importez dans votre environnement virtuel les packages nécessaires au script (requests, bs4, csv, future3), tels que présents dans le fichier requirements.txt
Il est possible d'utiliser la ligne de commande "pip install -r requirements.txt",
ou d'installer les packages un par un : "pip install requests"

### 3 - Lancez l'application : 
#### Commande terminal : python execution.py"
2 - Exécutez le script "execution.py" via la ligne de commande "python execution.py",
ou via pyCharm, Visual Studio Code ... (ou tout autre logiciel)



## Déroulement de l'appliaction :
Le fichier "functions.py" contient les fonctions d'extractions du contenu.
"execution.py" génère les dossiers des catégories et appelle les fonctions de "fonctions.py" afin d'écrire les informations souhaitées dans les CSV et télécharger les images.
* Extraction du chemin d'accès du répertoire
* Extraction des listes d'url de chque catégories (depuis l'index du site)
  * Extraction sur chaque page catégorie de l'ensemble des urls de livres
    * Extraction pour chaque page de livre de l'ensemble des informations souhaitées 
  * Création d'un dossier par catégorie
    * Création d'un fichier CSV par catégorie
    * Ecriture des en_têtes
    * Inscription dans le CSV des informations ed chaque livre
    * Téléchargement des images dans le dossier
L'application fonctionne avec le threading

## En savoir plus :
Les fonctions de "P02_01_01_functions.py" sont documentées via docstrings avec leurs utilisations, arguments et retours.

## *Contenu principaux : 
* fichier execution.py
* fichier functions.py
* fichier liengithub
* fichier requirements.txt
* fichier README.md