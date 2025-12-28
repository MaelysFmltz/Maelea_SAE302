SAE 3.02 / R3.09 : Conception d’une architecture distribuée avec routage en oignon

1. Présentation du projet

	Ce projet a été réalisé dans le cadre de la SAE 3.02 / R3.09 du BUT Réseaux & Télécommunications.
	
	L’objectif est de concevoir et implémenter une architecture distribuée permettant des communications anonymes, inspirée du routage en oignon (principe utilisé par TOR).
	
	Les messages échangés entre clients transitent par plusieurs routeurs intermédiaires.
	Chaque routeur ne connaît que son voisin direct et ne déchiffre qu’une seule couche du message.

2. Objectifs pédagogiques

	- Ce projet permet de mettre en œuvre les compétences suivantes :
	- Programmation client / serveur avec sockets
	- Gestion des connexions simultanées avec threading
	- Implémentation d’un chiffrement simplifié
	- Mise en place d’un routage multi-sauts
	- Utilisation d’une base de données MariaDB
	- Développement d’une interface graphique Qt
	- Respect des contraintes de sécurité et d’anonymisation

3. Architecture générale

	L’architecture du projet est composée de quatre éléments principaux :
	
		3.1 Master
		
			- Centralise les informations du réseau
   			- Enregistre les clients et les routeurs
			- Stocke les clés publiques dans une base MariaDB
			- Fournit aux clients la liste des routeurs disponibles
			
		3.2 Routeurs
		
			- Reçoivent les messages chiffrés
			- Déchiffrent une seule couche
			- Redirigent le message vers le prochain saut
			- Ne connaissent jamais l’origine complète ni la destination finale
		
		3.3 Clients
		
			- Interface graphique développée avec PyQt5
			- Permet d’envoyer et de recevoir des messages
			- Construit le message en plusieurs couches de chiffrement (oignon)
			- Choisit un chemin aléatoire de routeurs
		
		3.4 Base de données (MariaDB)
		
			Stocke les informations suivantes :
			
				- routeurs (nom, IP, port, clé publique)
				- clients (nom, IP, port, clé publique)

4. Technologies utilisées

	Langage : Python 3
	
	Bibliothèques autorisées : socket, threading, random, time, mariadb, PyQt5
	
	Base de données : MariaDB
	
	Systèmes : Linux (Master, Routeurs) / Windows ou Linux (Clients)
	
Aucune bibliothèque de cryptographie externe n’a été utilisée, conformément aux consignes.

5. Chiffrement et anonymisation

	Le chiffrement est volontairement simplifié et repose sur une opération XOR.
	
	Chaque routeur possède :
	
		- une clé privée
		- une clé publique (transmise au Master)
	
	Principe du routage en oignon :
	
		- Le client choisit un chemin de plusieurs routeurs
		- Le message est chiffré successivement avec les clés des routeurs
		- Chaque routeur enlève une couche et transmet le reste
		- Le dernier routeur envoie le message final au client destinataire
		
Ce mécanisme garantit que aucun routeur ne connaît l’intégralité du chemin et que l’anonymat des communications est respecté.

