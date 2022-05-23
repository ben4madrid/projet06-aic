# OPENCLASSROOMS - AIC
__________________________________________________________________
# Projet 06 : Participez à la vie de la communauté Open Source    #
__________________________________________________________________

## Script de Sauvegarde de notre serveur Web avec le CMS Wordpress et sa base de Donnée vers AWS S3 #

Le script permet de sauvegarder le dossier d'installation de wordpress en entier ainsi que le dump de la base de donnée Wordpress sur MariaDB

__________________________________________________________________
# Prérequis                                                      #
__________________________________________________________________

## Python ; Debian ; MariaDB
- Version Python  Utilisé    : 2.7.14  https://www.python.org/downloads/release/python-377/
- Version Debian  Utilisé    : 9.4.0   https://www.debian.org/distrib/netinst
- Version MariaDB Utilisé    : 10.1.18    https://go.mariadb.com/

## Installation du Serveur WEB sous Wordpress

- Fixer l'adresse IP de notre serveur web 
> Ouvrez le fichier ```/etc/network/interfaces```
Dans le fichier ```/etc/network/interfaces```, ajoutez les entrées suivantes et remplacez le caractère générique par l'adresse IPv4 principale du serveur :
```
auto eth0
iface eth0 inet static
address <ADRESSE IPV4 PRINCIPALE>
netmask <MASQUE SOUS RESEAU>
gateway <PASSERELLE>
```
> Pour redémarrer le réseau, entrez la commande suivante :
```/etc/init.d/networking restart```

- Mise à jour du système
```
apt update 
apt upgrade -y
```

- Installation librairie
```
apt install apache2 php libapache2-mod-php mysql-server php-mysql
apt install php-curl php-gd php-intl php-json php-mbstring php-xml php-zip
service apache2 start
service mysql start
```

- Création de la BDD mysql
```
mysql -u root -p
CREATE DATABASE wp_database; # Création de la table
CREATE USER user@localhost IDENTIFIED BY 'mot_de_passe'; # Création de l'user et du mot de passe
GRANT ALL PRIVILEGES ON wp_database.* TO user@localhost; 
FLUSH PRIVILEGES;
exit
```

- Installation de Wordpress
```
cd /var/www/html
wget https://wordpress.org/latest.tar.gz
tar xzvf latest.tar.gz 
chown -R www-data:www-data /var/www/html/*
```

## Accès depuis le navigateur
> - localhost/wordpress
> - Son IP (exemple : 192.168.1.150)


# Modules utilisés    
> -  os
> -  sys
> -  re
> -  subprocess
> -  tarfile
> -  datetime
> -  boto3
> -  time 

## Installing or updating the latest version of the AWS CLI
Installation du module AWS CLI version 2 https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

```
sudo apt install curl #Installation de la command CURL
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

# Création du compte AWS
Je suis débutant sur AWS. Comment créer et activer un nouveau compte AWS ?
https://aws.amazon.com/fr/premiumsupport/knowledge-center/create-and-activate-aws-account/

## Création de la clé d'accès
En haut à droite sélectionnez votre nom du compte :
> - Cliquez sur "Informations d'identification de sécurité"
> - Puis ouvrez l'onglet "Clés d'accès (ID de clé d'accès et clé d'accès secrète)"
> - Appuyez sur "Créer une clé d'accès"
> - Sauvegarde votre fichier.csv #La clé secrète peut être consultée ou téléchargée uniquement au moment de la création.

## Retour sur notre serveur WEB
Modifier le fichier de configuration AWS avec la commande suivante dans une distribution Linux
```
$ aws configure 

AWS Access Key ID [None]: VOTRE ID
AWS Secret Access Key [None]: VOTRE KEY
Default region name [None]: VOTRE REGION #Exemple : eu-west-3
Default output format [None]: python
```
## Création d'un bucket sur AWS S3
- Pour télécharger vos données (photos, vidéos, documents, etc.) sur Amazon S3, vous devez d'abord créer un compartiment S3 dans l'une des régions AWS.
- Un compartiment est un conteneur pour les objets stockés dans Amazon S3. Vous pouvez stocker n'importe quel nombre d'objets.
- Suivre la documentation AWS https://docs.aws.amazon.com/fr_fr/AmazonS3/latest/user-guide/create-bucket.html 


# MariaDB
- Création d'un utilisateur avec les droits pour effectuer le dump de la base de donnée du site wordpress
- Pas de chiffrement des credentials __ATTENTION AUX DROITS__ donnés

## Creation du MariaDB BUMP ########
```python
def WPDBDump(db_details):

    USER = db_details['mon_user_admin'] 	#User admin de la BDD
    DBPASSWORD = db_details['mon_mot_de_passe'] #Mot de passe de la BDD
    DBHOST = db_details['localhost'] 		#BDD Héberger sur la machine
    DBNAME = db_details['ma_base_de_donnees']	#Nom de ta table BDD
    [...]
```

__________________________________________________________________
# Exécution du script                                                  #
__________________________________________________________________

## Variable à modifier 
```python
- HOMEPATH = 'Dossier de votre site Wordpress' 		#Exemple : '/var/www/html'
- BACKUP_PATH = 'chemin de votre dossier de sauvegarde' #Exemple : '/home/user/Sauvegarde'
- bucket = "NOM BUCKET S3" 				#Le nom de votre bucket sur AWS S3
```
## Exécution
- Le script exécute vérifie la présense du dossier Wordpress puis éxécute toute les fonctions dans le code principal.
```python
python ./backup.py

python3 ./backup.py
```

## Particularité du script


  - Expression Regulière pour extraire les idenfiants permettant le dump de la BDD
    > def WPregex(HOMEPATH):
  - Compression des fichiers à sauvegarder en tar.Bz2
    > def WPBackupTar
  - Temps d'attente entre l'éxécution de la fonction de suppréssion des fichiers local et l'upload sur S3 (*L125*)
    > Cela permet d'assurer que l'upload est bien fini avant de le tester
      
	  
#### OpenClassrooms - AIC - Benjamin M - 2022 ###
#### Remerciement à tous mes mentors sur OC ###


