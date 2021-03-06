#!/bin/python

###########################################################################
#"""Backup.py: Description """

_author  = "Benjamin MADRID"
_version = "2.3"
_date    = "10/05/22"

#_Modification du code V2.3
#Ajout de la variable.ROOTDIR pour execution du script avec Crontab

##########################################################################

# Importation des modules nécessaires à l'exécution du script
import os
import sys
import re
import subprocess
import tarfile
import datetime
import logging
import boto3
import time
from boto3 import client

##### Variables Initialisations #######

# Définition des variables
HOMEPATH = '/ton/chemin/dossier/wordpress' #Mettre le chemin du dossier Wordpress
BACKUP_DATE = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
BACKUP_PATH = '/ton/chemin/dossier/sauvegarde/wordpress/' #Mettre le chemin du dossier de Sauvegarde
BACKUP_NAME =  BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)
bucket = "NOM_BUCKET" #Mettre le nom de ton Bucket S3
ROOTDIR = '/usr/local/bin/'

##### Regex pour récupérer les informations de connexion à la base de données #######

    # Il prend le chemin vers le fichier wp-config.php comme argument, l'ouvre, le lit, puis utilise regex
    # pour extraire le nom de la base de données, l'utilisateur, le mot de passe et l'hôte
    # :param HOMEPATH : Le chemin vers l'installation de WordPress
    # :return : un dictionnaire avec les clés et les valeurs de la base de données, de l'utilisateur, du mot de passe et de l'hôte
    
def WPregex(HOMEPATH):
    wpconfigfile = os.path.normpath(HOMEPATH +"/wp-config.php")
    with open(wpconfigfile) as fh:
        wpconfigcontent=fh.read()
    regex_db = r'define\(\s*?\'DB_NAME\'\s*?,\s*?\'(?P<DB>.*?)\'\s*?\);' # Regex to extract db name info
    regex_user = r'define\(\s*?\'DB_USER\'\s*?,\s*?\'(?P<USER>.*?)\'\s*?\);' # Regex to extract db user
    regex_pass = r'define\(\s*?\'DB_PASSWORD\'\s*?,\s*?\'(?P<PASSWORD>.*?)\'\s*?\);' # Regex to extract db password
    regex_host = r'define\(\s*?\'DB_HOST\'\s*?,\s*?\'(?P<HOST>.*?)\'\s*?\);'         # Regex to extract db host
    database = re.search(regex_db,wpconfigcontent).group('DB')
    user = re.search(regex_user,wpconfigcontent).group('USER')
    password = re.search(regex_pass,wpconfigcontent).group('PASSWORD')
    host = re.search(regex_host,wpconfigcontent).group('HOST')
    return {'ma_base_de_donnees':database, #Nom de ta table BDD
                'mon_user_admin':user, #User admin de la BDD
                'mon_mot_de_passe':password, #Mot de passe de la BDD
                'localhost':host #BDD Héberger sur la machine
                }

##### Creation du MariaDB BUMP ########

# Il prend un dictionnaire comme argument et renvoie une chaîne
# :param db_details : il s'agit d'un dictionnaire contenant les détails de la base de données
# :return : Le nom du fichier de sauvegarde

def WPDBDump(db_details):

    USER = db_details['mon_user_admin'] #User admin de la BDD
    DBPASSWORD = db_details['mon_mot_de_passe'] #Mot de passe de la BDD
    DBHOST = db_details['localhost'] #BDD Héberger sur la machine
    DBNAME = db_details['ma_base_de_donnees'] #Nom de ta table BDD
    BACKUP_NAME_SQL = os.path.normpath(os.path.join(BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)+'.sql')) # definition name of backup
    cmd = "mysqldump -h{} -u{} -p{} {} > {} ".format(\
        DBHOST, USER, DBPASSWORD, DBNAME, BACKUP_NAME_SQL)
    subprocess.check_output(cmd,shell=True)
    print('Dump OK ..')
    return(BACKUP_NAME_SQL)


####### Fichiers Compressés ############

# Il crée une archive tar.bz2 du dossier wordpress et la sauvegarde de la base de données
# :param HOMEPATH : le chemin d'accès au dossier que vous souhaitez sauvegarder
# :param BACKUP_BDD : le chemin vers le fichier de sauvegarde de la base de données
# :return: L'objet tarfile

def WPBackupTar(HOMEPATH,BACKUP_BDD):

    backup_bz2 = tarfile.open(BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)+'.tar.bz2','w:bz2') # path of  local save folder (tar.bz2)
    backup_bz2.add(HOMEPATH)
    backup_bz2.add(BACKUP_BDD)
    backup_bz2.close()
    print('zip ok')
    return(backup_bz2)


######## Fichier Copie vers S3 ########

# Il prend un nom de fichier en entrée et le télécharge sur S3
# :param bz2FILE : nom du fichier à télécharger sur S3
# :return : Le nom du fichier qui a été chargé sur S3

def CopietoS3(bz2FILE):

    cmd = "{}aws s3 cp {} s3://{}/ ".format(\
       ROOTDIR, bz2FILE, bucket) # Shell cmd to updload the file in AWS S3
    subprocess.check_output(cmd,shell=True)
    print('Fichier',bz2FILE,'SQL et FICHIER sont uploade')
    return(bz2FILE)



######### Verification du fichier dans AWS S3 ############

# Cette fonction prend un fichier bz2 comme argument et renvoie la taille du fichier en octets
# :param bz2FILE : le nom du fichier que vous souhaitez vérifier dans S3
# :return : Le file_bucket est renvoyé

def veriftoS3(bz2FILE):

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    file_bucket = s3.ObjectSummary(my_bucket,bz2FILE)
    return (file_bucket)

######### Suppression du fichier en LOCAL ############

# Si la variable veriftoS3 existe, supprimez les fichiers bz2FILE et BACKUP_BDD."
# La fonction s'appelle ainsi :
# Fileremove(bz2FILE,BACKUP_BDD,veriftoS3)
# La variable veriftoS3 est définie dans la fonction S3_upload
# :param bz2FILE : le nom du fichier que vous souhaitez télécharger sur S3
# :param BACKUP_BDD : Le nom du fichier de sauvegarde
# :param veriftoS3 : Ceci est la sortie de la fonction upload_file

def Fileremove(bz2FILE,BACKUP_BDD,veriftoS3):
    try:
       veriftoS3
    except NameError:
          print('mauvais fichier copie')

    else:
        os.remove(bz2FILE)
        os.remove(BACKUP_BDD)
        print('fichier local supprime')


####### Main Code ################
print ('##################### Script Backup running...###########################')
####### Check if the path existing ################

if os.path.isdir(HOMEPATH):
    print("Le Dossier",HOMEPATH, "existe")
    print ('##################### Requete regex BDD ###########################')
    DBINFO = WPregex(HOMEPATH)
    print ('##################### Dump BDD ###########################')
    BACKUP_BDD = WPDBDump(DBINFO)
    print ('##################### Dossiers Wordpress et BDD ZIP ###########################')
    WPBackupTar(HOMEPATH,BACKUP_BDD)
    print ('##################### Dossier Copie Vers AWS S3 ###########################')
    bz2FILE = (BACKUP_PATH+'sauvegarde'+str(BACKUP_DATE)+'.tar.bz2')
    CopietoS3(bz2FILE)
    print ('##################### Verification des fichiers sur AWS ###########################')
    veriftoS3(bz2FILE)
    time.sleep(8) # Waiting time to check the copy before file remove
    remove_on = veriftoS3(bz2FILE)
    print ('##################### Supression des fichiers Local###########################')
    Fileremove(bz2FILE,BACKUP_BDD,veriftoS3)

else:
    print("dossier", HOMEPATH, "n'existe pas")





