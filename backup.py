#!/bin/python

###########################################################################
#"""Backup.py: Description """

_author  = "Benjamin MADRID"
_version = "2.3"
_date    = "10/05/22"

#_Modification du code V2.3
#Ajout de la variable.ROOTDIR pour execution du script avec Crontab

##########################################################################

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
HOMEPATH = '/var/www/html/wordpress'
BACKUP_DATE = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
BACKUP_PATH = '/home/sauvegarde/wordpress/'
BACKUP_NAME =  BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)
bucket = "projet06"
ROOTDIR = '/usr/local/bin/'

##### Regex to get back login information to Database #######

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
    return {'wpdatabase':database,
                'wpadmin':user,
                'wemakesure':password,
                'localhost':host
                }

##### Creation du MariaDB BUMP ########

def WPDBDump(db_details):

    USER = db_details['wpadmin']
    DBPASSWORD = db_details['wemakesure']
    DBHOST = db_details['localhost']
    DBNAME = db_details['wpdatabase']
    BACKUP_NAME_SQL = os.path.normpath(os.path.join(BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)+'.sql')) # definition name of backup
    cmd = "mysqldump -h{} -u{} -p{} {} > {} ".format(\
        DBHOST, USER, DBPASSWORD, DBNAME, BACKUP_NAME_SQL)
    subprocess.check_output(cmd,shell=True)
    print('Dump OK ..')
    return(BACKUP_NAME_SQL)


####### Fichier Compressé ############
def WPBackupTar(HOMEPATH,BACKUP_BDD):

    backup_bz2 = tarfile.open(BACKUP_PATH+'/sauvegarde'+str(BACKUP_DATE)+'.tar.bz2','w:bz2') # path of  local save folder (tar.bz2)
    backup_bz2.add(HOMEPATH)
    backup_bz2.add(BACKUP_BDD)
    backup_bz2.close()
    print('zip ok')
    return(backup_bz2)


######## Fichier Copie vers S3 ########
def CopietoS3(bz2FILE):

    cmd = "{}aws s3 cp {} s3://{}/ ".format(\
       ROOTDIR, bz2FILE, bucket) # Shell cmd to updload the file in AWS S3
    subprocess.check_output(cmd,shell=True)
    print('Fichier',bz2FILE,'SQL et FICHIER sont uploade')
    return(bz2FILE)



######### Verification du fichier dans AWS S3 ############
def veriftoS3(bz2FILE):

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    file_bucket = s3.ObjectSummary(my_bucket,bz2FILE)
    return (file_bucket)

######### Suppression du fichier en LOCAL ############
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
print ('##################### Backup running...###########################')
####### Check if the path existing ################

if os.path.isdir(HOMEPATH):
    print("Le Dossier",HOMEPATH, "existe")
    print ('##################### Requete regex BDD ###########################')
    DBINFO = WPregex(HOMEPATH)
    print ('##################### Dump BDD ###########################')
    BACKUP_BDD = WPDBDump(DBINFO)
    print ('##################### ZIP des deux fichier ###########################')
    WPBackupTar(HOMEPATH,BACKUP_BDD)
    print ('##################### Copie Vers AWS S3 ###########################')
    bz2FILE = (BACKUP_PATH+'sauvegarde'+str(BACKUP_DATE)+'.tar.bz2')
    CopietoS3(bz2FILE)
    print ('##################### Verification des fichiers sur AWS ###########################')
    veriftoS3(bz2FILE)
    time.sleep(8) # Waiting time to check the copy before file remove
    remove_on = veriftoS3(bz2FILE)
    print ('##################### Supression fichiers Local###########################')
    Fileremove(bz2FILE,BACKUP_BDD,veriftoS3)

else:
    print("dossier", HOMEPATH, "n'existe pas")





