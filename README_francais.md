# Script de Monitoring JVM via SSH pour Nagios

Ce script en Python permet de surveiller une JVM distante (par exemple, Tomcat/Catalina ou toute autre JVM) en se connectant via SSH. Il interroge diverses métriques (CPU, RAM, Garbage Collector, Heap, nombre de classes chargées et threads actifs) afin de faciliter l'intégration avec Nagios.

## Fonctionnalités

- **Connexion SSH :** Se connecte à un hôte distant en utilisant une clé SSH.
- **Recherche du processus Java :** Identifie le PID d'un processus Java via `pgrep -f java`.
- **Vérifications des métriques :**
  - **CPU :** Utilisation du CPU du processus Java.
  - **RAM :** Utilisation de la mémoire.
  - **Garbage Collector :** État du garbage collector via `jstat -gc`.
  - **Heap :** Taille et utilisation du heap via `jstat -gccapacity`.
  - **Classes :** Nombre de classes chargées via `jstat -class`.
  - **Threads :** Nombre de threads actifs via `ps -L`.

## Prérequis

- **Python 3**
- **Bibliothèque Paramiko :**  
  Installez-la avec la commande suivante :
  ```bash
  pip install paramiko
Outils nécessaires sur l'hôte distant :

pgrep

ps

jstat

Utilisation
Exécutez le script en fournissant les arguments requis :

bash
Copier
./script.py -H <hôte> -i <chemin_clé_ssh> -m <mode> [options]
Arguments principaux
-H, --host : (Obligatoire) Hôte à interroger.

-i, --identity : (Obligatoire) Chemin vers la clé SSH.

-m, --mode : (Obligatoire) Mode de vérification. Choix possibles :

cpu : Vérifier l'utilisation CPU.

ram : Vérifier l'utilisation RAM.

gc : Vérifier l'état du Garbage Collector.

heap : Afficher la taille et l'utilisation du Heap.

classes : Afficher le nombre de classes chargées.

threads : Afficher le nombre de threads actifs.

Options complémentaires
-w, --warning : Seuil warning pour les métriques (par défaut : 80.0).

-c, --critical : Seuil critical pour les métriques (par défaut : 90.0).

-u, --user : Utilisateur SSH (par défaut : root).

--debug : Active le mode débug (affichage d'informations détaillées).

--output : Format de sortie : short pour un résultat court ou long pour un résultat détaillé (par défaut : short).

Exemple d'exécution
Pour vérifier l'utilisation CPU sur l'hôte 192.168.1.100 avec l'utilisateur admin, une clé SSH située à /home/user/.ssh/id_rsa et des seuils warning à 75% et critical à 90%, en mode débug et sortie détaillée :

bash
Copier
./script.py -H 192.168.1.100 -i /home/user/.ssh/id_rsa -m cpu -w 75 -c 90 -u admin --output long --debug
Codes de sortie (selon la convention Nagios)
0 : OK

1 : WARNING

2 : CRITICAL

3 : UNKNOWN (en cas d'erreur, par exemple : échec de la connexion SSH ou absence de processus Java)

Contribution
Si vous souhaitez contribuer, corriger un bug ou améliorer le script, n'hésitez pas à ouvrir une issue ou à proposer une pull request.

Licence
Ce script est distribué "tel quel", sans garantie d'aucune sorte. Vous êtes libre de l'utiliser, le modifier et le redistribuer selon vos besoins.

© Julien Charbonnel, Conseil départemental de Haute-Loire 2025, assisté par CHATGPT.
