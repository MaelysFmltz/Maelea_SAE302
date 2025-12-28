SAE 3.02 / R3.09 : Conception d’une architecture distribuée avec routage en oignon

1. Présentation du projet

Ce projet a été réalisé dans le cadre de la SAE 3.02 du BUT Réseaux & Télécommunications.
Il consiste à concevoir une architecture distribuée permettant l’échange de messages anonymisés entre clients, en s’inspirant du principe du routage en oignon.
	
L’architecture repose sur trois types d’entités :

	- un Master central
	- plusieurs Routeurs
	- plusieurs Clients avec interface graphique

Le système permet à un client d’envoyer un message à un autre client en passant par plusieurs routeurs choisis aléatoirement, chaque routeur ne connaissant que l’étape suivante.

2. Architecture générale : Rôles des composants

Master

- Centralise les informations
- Enregistre les clients et les routeurs
- Stocke les clés publiques dans une base MariaDB
- Fournit la liste des clients et routeurs aux clients

Routeur

- Possède une paire de clés (publique / privée)
- Déchiffre une couche du message
- Transmet le message au prochain nœud

Client

- Interface graphique Qt
- Enregistre sa clé publique auprès du Master
- Récupère la topologie (clients et routeurs)
- Construit le message en oignon
- Envoie le message sans bloquer l’interface

3. Librairies utilisées

Librairies autorisées : socket, threading, PyQt5, mariadb (connecteur Python), random, time

Librairies interdites (non utilisées) : json, cryptography, toute librairie de chiffrement externe

4. Structure du projet

Maelea_SAE302/
│
├── Source/
│   ├── Master/
│   │   ├── code/
│   │   │   └── server_master.py
│   │   └── logs/
│   │
│   ├── Router/
│   │   ├── code/
│   │   │   ├── router.py
│   │   │   ├── generate_keys.py
│   │   │   └── send_pub_key.py
│   │   └── keys/
│   │
│   └── Client/
│       ├── code/
│       │   ├── client.py
│       │   └── generate_keys.py
│       └── keys/
│
├── database/
│   └── schema.sql
│
└── README.md

5. Base de données MariaDB

La base de données est utilisée par le Master pour stocker les clés publiques.
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
Il suffit de suivre les étapes dans l’ordre, sans connaissances particulières.

7.1 Récupération du projet depuis GitHub

Installation de Git :

	sudo apt update
	sudo apt install git -y

Cloner le projet :

	git clone https://github.com/VOTRE_PSEUDO/Maelea_SAE302.git
	cd Maelea_SAE302

7.2 Installation des dépendances communes	

Installer Python 3 et pip :

	sudo apt install python3 python3-pip -y

Vérifier :

	python3 --version

Installer PyQt5 :

	pip install PyQt5
	
Installer le connecteur MariaDB pour Python :

	pip install mariadb
	

PARTIE 1 — MASTER	

7.3 Installation de MariaDB (sur la VM Master)

Installer MariaDB :

	sudo apt update
	sudo apt install mariadb-server mariadb-client -y

Démarrer le service :

	sudo systemctl start mariadb
	sudo systemctl enable mariadb

Sécurisation de MariaDB :

	sudo mysql_secure_installation

Réponses recommandées :

	Set root password → YES
	Remove anonymous users → YES
	Disallow root login remotely → YES
	Remove test database → YES
	Reload privilege tables → YES

	
7.4 Création de la base de données

Connexion à MariaDB :

	mariadb -u root -p

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

7.5 Lancement du Master

Se placer dans le dossier :

	cd Source/Master/code

Lancer le Master :

	python3 server_master.py

Saisir :

	Port d’écoute : 5000
	DB host : localhost
	DB user : maelea
	DB password : sae302
	DB name : sae302
	
Message attendu :

	[MASTER] En écoute sur le port 5000

PARTIE 2 — ROUTEURS

7.6 Lancement des routeurs (minimum 3)

Se placer dans le dossier routeur :

	cd Source/Router/code

Génération des clés du routeur :

	python3 generate_keys.py

Envoi de la clé publique au Master :

	python3 send_pub_key.py

Exemple :

	Nom : R1
	Port : 5001
	IP : 127.0.0.1
	IP Master : 127.0.0.1
	Port Master : 5000

Port du Master est celui qui a été choisie préalablement dans la configuration du master

Lancement du routeur :

	python3 router.py

Message attendu :

	[R1] En écoute sur le port 5001

Répéter exactement les mêmes étapes pour R2, R3, etc.
Il faudra changé le nom et le port.

PARTIE 3 — CLIENTS

7.7 Lancement des clients

Se placer dans le dossier client:

	cd Source/Client/code

Génération des clés client :

	python3 generate_keys.py

Lancement du client :

	python3 client.py

	Exemple :
	Nom : C1
	Port : 6001
	IP Master : 127.0.0.1
	Port Master : 5000


Une interface graphique s’ouvre.

Lancer un second client :

Même procédure avec :
	
	Nom : C2
	Port : 6002




