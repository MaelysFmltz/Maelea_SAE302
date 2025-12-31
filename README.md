SAE 3.02 / R3.09 : Conception d’une architecture distribuée avec routage en oignon

1. Présentation du projet

Ce projet a été réalisé dans le cadre de la SAE 3.02 du BUT Réseaux & Télécommunications.
Il a pour objectif de concevoir une architecture distribuée permettant l’échange de messages anonymisés entre clients, en s’inspirant du principe du routage en oignon (Onion Routing) utilisé notamment par le réseau TOR.
	
L’architecture repose sur trois types d’entités :

	- un Master central
	- plusieurs Routeurs
	- plusieurs Clients avec interface graphique

Le système permet à un client d’envoyer un message à un autre client en passant par plusieurs routeurs choisis aléatoirement.
Chaque routeur ne connaît que l’étape suivante, et n’a aucune information sur l’origine ou la destination finale du message.

2. Architecture générale : Rôles des composants

Master

- Centralise les informations
- Enregistre les clients et les routeurs
- Stocke les clés publiques dans une base MariaDB
- Fournit la liste des clients et routeurs aux clients

Le Master ne participe jamais au transit des messages.

Routeur

- Possède une paire de clés (publique / privée)
- Déchiffre une couche du message
- Transmet le message au prochain nœud

Un routeur ne connaît jamais l’expéditeur ni le destinataire final.

Client

- Interface graphique Qt permetant l'envoi de messages ver un destinater (un autre client)
- Enregistre sa clé publique auprès du Master
- Récupère la topologie (clients et routeurs)
- Construit le message en oignon de sorte a les securiser
- Envoie le message sans bloquer l’interface

Le client est responsable de tout le chiffrement initial.

3. Librairies utilisées

Librairies autorisées : socket, threading, PyQt5, mariadb (connecteur Python), random, time

Librairies interdites (non utilisées) : json, cryptography, toute librairie de chiffrement externe

4. Structure du projet

Le dossier Master regroupe le programme principal du réseau.
Il contient le script server_master.py, qui gère l’enregistrement des routeurs et des clients, stocke les informations dans la base de données MariaDB et fournit la liste des routeurs aux clients.
Un sous-dossier logs est présent afin de conserver les journaux d’exécution du Master (connexions, erreurs, événements).

Le dossier Router contient le code des routeurs virtuels.
Chaque routeur dispose d’un script principal (router.py) qui reçoit les messages, enlève une couche de chiffrement et les transmet au prochain nœud.
Un script de génération de clés (generate_keys.py) permet de créer la paire de clés du routeur, et un script (send_pub_key.py) est utilisé pour envoyer la clé publique au Master.
Les clés du routeur sont stockées dans un dossier keys.

Le dossier Client contient l’application client.
Le script client.py correspond à l’interface graphique Qt permettant à un utilisateur d’envoyer et de recevoir des messages anonymisés.
Un script de génération de clés est également présent afin de créer les clés du client.
Les clés sont stockées dans le dossier keys.

Enfin, le dossier database contient le fichier schema.sql, qui permet de créer la base de données MariaDB ainsi que les tables nécessaires au fonctionnement du projet.

Le fichier README.md regroupe l’ensemble de la documentation du projet : présentation, installation, utilisation, choix techniques et explication du fonctionnement.

5. Base de données MariaDB

La base de données est utilisée par le Master pour stocker les clés publiques des routeurs et des clients.
Elle n’est pas stockée sur GitHub, seul le script SQL est fourni qui s'appel : schema.sql

6. Algorithme de chiffrement (routage en oignon)

Le chiffrement utilisé dans ce projet est volontairement simple et pédagogique.
Il a pour but d’illustrer le principe du routage en oignon, et non de proposer une solution de sécurité réelle.

Principe :

- Chaque routeur possède une clé privée et une clé publique
- Le client chiffre le message plusieurs fois, avec les clés publiques des routeurs choisis
- Chaque routeur enlève une seule couche de chiffrement, puis transmet le message
- Un routeur ne connaît que le prochain nœud, jamais l’origine ni la destination finale
- Le chiffrement repose sur une opération XOR entre le message et une clé.

Avantages :

- Facile à comprendre
- Permet de visualiser clairement le routage en oignon
- Respecte les contraintes du projet

Limites :

- Chiffrement non sécurisé dans un contexte réel
- Utilisation uniquement pédagogique
  
7. Installation et utilisation du projet (pas à pas)

Cette section décrit l’installation complète et l’utilisation du projet, dans l’ordre logique de fonctionnement du système.
Il suffit de suivre les étapes dans l’ordre, sans connaissances particulières. Les VMs devront être sur le même réseau en Réseau privé hôte avec un NAT.

7.1 Récupération du projet depuis GitHub

Installation de Git :

	sudo apt update
	sudo apt install git -y

ou si problème :
	
	su -
	apt update
	usermod -aG sudo (user)
	reboot

Cloner le projet :

	git clone https://github.com/votrenom/Maelea_SAE302.git
	cd Maelea_SAE302
	git checkout -b master origin/master
	
Cette commande est à faire parce que le branch est sur master et pas sur main (default)

7.2 Installation des dépendances communes	

Installer Python 3 et pip :

	sudo apt install python3 python3-pip -y

Vérifier :

	python3 --version

Installer venv :

	sudo apt install python3-venv python3-full -y
	

PARTIE 1 — MASTER	

7.3 Installation de MariaDB (sur la VM Master)

Installer MariaDB :

	sudo apt update
	sudo apt install -y libmariadb-dev python3-dev
	sudo apt install mariadb-server mariadb-client -y

Démarrer le service :

	sudo systemctl start mariadb
	sudo systemctl enable mariadb


7.4 Création de la base de données

Connexion à MariaDB :

	sudo mariadb

Création de la base et des tables :

Copier-coller le fichier schema.sql dans database:

	CREATE DATABASE sae302;
	USE sae302;
	
	CREATE TABLE routeurs (
	    id INT AUTO_INCREMENT PRIMARY KEY,
	    router_name VARCHAR(20) UNIQUE,
	    ip VARCHAR(50),
	    port INT,
	    public_key TEXT
	);
	
	CREATE TABLE clients (
	    id INT AUTO_INCREMENT PRIMARY KEY,
	    client_name VARCHAR(20) UNIQUE,
	    ip VARCHAR(50),
	    port INT,
		public_key TEXT
	);

Création d’un utilisateur dédié :

	CREATE USER 'maelea'@'localhost' IDENTIFIED BY 'sae302';
	GRANT ALL PRIVILEGES ON sae302.* TO 'maelea'@'localhost';
	FLUSH PRIVILEGES;
	EXIT;

Création d'un environnement virtuel :

	cd Source/Master
	python3 -m venv venv 
	
7.5 Lancement du Master

Vérification de l'interface :

	ip a

S'il n'y a pas d'ip il faut faire :

	sudo apt install isc-dhcp-client
	sudo dhclient enp0s"3" 

Activier l'environnement :

	source venv/bin/activate

Installation du connecteur MariaDB Python :

	pip install mariadb

Lancer le Master :

	cd code
	python3 server_master.py

Saisir :

	Port d’écoute : 5000
	
Message attendu :

	[MASTER] En écoute sur le port 

Création du fichier logs :

	mkdir logs

PARTIE 2 — ROUTEURS

7.6 Lancement des routeurs (minimum 3)

A répéter pour chaque routeur...

Mise à jour du système :

	sudo apt update

Installation des outils :

	sudo apt install -y git python3 python3-venv python3-pip

Cloner le projet :

	git clone https://github.com/votrenom/Maelea_SAE302.git
	cd Maelea_SAE302
	git checkout -b master origin/master
	
Se placer dans le dossier routeur :

	cd Source/Router

Vérification des fichiers :

	ls

(code/, keys/)

S'il n'y a pas keys alors :
	
	mkdir keys 

Aller dans le dossier de code :

	cd code

Génération des clés du routeur :

	python3 generate_keys.py

Résultat : [ROUTEUR] Clés générées.

Les fichiers suivants sont crées :

	Source/Router/keys/private.key
	Source/Router/keys/public.key

Lancement du routeur :

	python3 router.py

Exemple :
	
	Nom du routeur : R1
	Port d'écoute : 5001

Message attendu :

	[R1] En écoute sur le port 5001

Dans un autre Terminal :

Envoi de la clé publique au Master :
	
	cd Maelea_SAE302/Source/Router/code
	python3 send_pub_key.py

Exemple :

	Nom  du routeur : R1
	IP du routeur : (faire un "ip a")
	Port du routeur : 5001
	IP du Master : (faire "ip a" sur le Master)
	Port Master : 5000

Port du Master est celui qui a été choisie préalablement dans la configuration du master

Résultat attendu sur le Routeur : 

	[R1] Clé publique envoyée

Résultat attendu sur le Master:

	[MASTER] Routeur enregistré : R1 (adresse ip du routeur):5001

Après l’exécution de send_pub_key.py sur le routeur la clé publique du routeur doit être stockée dans la base MariaDB du Master, dans "routeurs".

Sur le Master :

	sudo mariadb
Puis :

	USE sae302;
	SELECT * FROM routeurs;

Le Master stocke les clés publiques et les adresses des routeurs dans une base MariaDB.
Les clients interrogent ensuite le Master pour récupérer ces informations afin de construire les messages en oignon.


Répéter exactement les mêmes étapes pour R2, R3, etc.
Il faudra changé le nom et le port, par exemple ( R2 -> 5002, R3 -> 5003)






PARTIE 3 — CLIENTS

A répéter pour chaque client (C1,C2...)

Ouvrir un navigateur internet et aller sur le site : 

	https://www.python.org/downloads/windows

Télécharger Python 3 (version stable) et lancer l’installateur.

IMPORTANT : cocher la case « Add Python.exe to PATH »

Cliquer sur « Install Now »

Attendre la fin de l’installation.

Vérifier l’installation :

Ouvrir PowerShell et taper :

	python –-version
	pip –-version
	
Les versions doivent s’afficher sans erreur.

INSTALLATION DE GIT:

Aller sur : https://git-scm.com/download/win

Télécharger Git et lancer l’installation

Vérifier Git :

	git –version
	
Ouvrir PowerShell :

Se placer dans le dossier Documents :

	cd Documents

Cloner le projet :

	git clone https://github.com/votrenom/Maelea_SAE302.git
	cd Maelea_SAE302
	git checkout -b master origin/master

Vérifier la structure :

	ls

On doit voir au minimum :
	
	Source
	README.md
	database

Se placer dans le dossier client:

	cd Source/Client

Vérification des fichiers :

	ls

(code/, keys/)

S'il y a que code alors on doit crée keys :

	mkdir keys

Créer l’environnement :

	python -m venv venv

Si ça ne fonctionne pas alors il faudra ouvrir Powershell en administrateur, puis taper :

	Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Quand Windows demande confirmation :

	O

Cette commande permet d'autoriser les scripts uniquement pour l'utilisateur.

Puis rouvrir Powershell normal et relancer la commande.
	
Activer l’environnement virtuel :

	venv\Scripts\activate

Il doit avoir affiché (venv)

Installer PyQt5 (interface graphique) :

	pip install PyQt5

Aller dans le dossier de code :

	cd code

Génération des clés du client:

	python generate_keys.py

Résultat : [CLIENT] Clés générées.

Les fichiers suivants sont crées :

	Source/Client/keys/private.key
	Source/Client/keys/public.key

Installation de PyQt (interface graphique)

Lancement du client :

	python client.py

	Exemple :
	Nom du client : C1
	Port du clientv: 6001
	IP Master : (faire un ip a sur master)
	Port Master : 5000


Une interface graphique s’ouvre automatiquement.

Actions automatiques :

- Le client s’enregistre auprès du Master
- Sa clé publique est envoyée
- Le Master mémorise le client

Sur Master, un message apparaît :

	[MASTER] Client enregistré : C1 (ip du C1):6001

Il faut également sur Master ouvrir un terminal et taper :

	sudo mariadb
	USE sae302;
	SELECT * FROM clients;

Après le lancement d’un client, il faut vérifier sur le Master que sa clé publique est bien stockée dans la base MariaDB grâce à une requête SELECT.
Cela garantit que les informations sont persistantes et accessibles aux autres composants. Puis nous pourrons lancer un second client...


Lancer un second client :

Même procédure avec :
	
	Nom : C2
	Port : 6002

Puis quand au minimum 2 clients ont été crée, il faut aller dans l’interface d'un des clients (pour exemple C1) :

Cliquer sur « Rafraîchir la liste » pour voir les autres clients

	Sélectionner un destinataire (C2)
	Écrire un message
	Cliquer sur « Envoyer »

Le message est automatiquement chiffré en plusieurs couches, envoyé au premier routeur, transmis anonymement et déchiffré uniquement par le client final.






