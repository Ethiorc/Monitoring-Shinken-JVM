#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2025 Julien Charbonnel - Département de la Haute Loire
#
# Version: 1.0
# Date: 2025-03-25
#
# Description:
#   Script de monitoring Nagios pour JVM (Tomcat/Catalina ou autre JVM).
#   Ce script se connecte via SSH pour interroger plusieurs métriques :
#     - CPU, RAM, Garbage Collector
#     - Heap (taille et utilisation)
#     - Nombre de classes chargées
#     - Nombre de threads actifs
#
# Usage:
#   python3 <script_name>.py [options]
#

import argparse
import paramiko
import sys

def get_jvm_pid(ssh, debug):
    """
    Recherche un processus Java sur le serveur distant en utilisant 'pgrep -f java'.
    Si plusieurs processus sont trouvés, le premier est utilisé.
    """
    command = "pgrep -f java"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Résultat de pgrep: {output}")
    pids = output.split()
    if not pids:
        print("UNKNOWN - Aucun processus Java trouvé sur le serveur")
        sys.exit(3)
    return pids[0]

def check_cpu(ssh, pid, warning, critical, output_mode, debug):
    """
    Vérifie l'utilisation CPU du processus Java via la commande ps.
    """
    command = f"ps -p {pid} -o %cpu --no-headers"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie ps: {output}")
    try:
        cpu_usage = float(output)
    except Exception:
        print("UNKNOWN - Erreur lors de la récupération de l'utilisation CPU")
        sys.exit(3)
    
    status = 0
    status_text = "OK"
    if cpu_usage >= critical:
        status = 2
        status_text = "CRITICAL"
    elif cpu_usage >= warning:
        status = 1
        status_text = "WARNING"
    
    if output_mode == "short":
        result = f"{status_text} - CPU: {cpu_usage:.2f}%"
    else:
        result = (f"{status_text} - CPU usage: {cpu_usage:.2f}% | "
                  f"thresholds: warning={warning}%, critical={critical}% | "
                  f"performance data: cpu={cpu_usage:.2f}%;{warning};{critical}")
    print(result)
    sys.exit(status)

def check_ram(ssh, pid, warning, critical, output_mode, debug):
    """
    Vérifie l'utilisation RAM du processus Java via la commande ps.
    """
    command = f"ps -p {pid} -o %mem --no-headers"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie ps: {output}")
    try:
        mem_usage = float(output)
    except Exception:
        print("UNKNOWN - Erreur lors de la récupération de l'utilisation RAM")
        sys.exit(3)
    
    status = 0
    status_text = "OK"
    if mem_usage >= critical:
        status = 2
        status_text = "CRITICAL"
    elif mem_usage >= warning:
        status = 1
        status_text = "WARNING"
    
    if output_mode == "short":
        result = f"{status_text} - RAM: {mem_usage:.2f}%"
    else:
        result = (f"{status_text} - RAM usage: {mem_usage:.2f}% | "
                  f"thresholds: warning={warning}%, critical={critical}% | "
                  f"performance data: ram={mem_usage:.2f}%;{warning};{critical}")
    print(result)
    sys.exit(status)

def check_gc(ssh, pid, warning, critical, output_mode, debug):
    """
    Vérifie l'état du garbage collector via la commande jstat.
    On extrait la colonne OC (Old Capacity) et OU (Old Used) pour calculer un ratio.
    """
    command = f"jstat -gc {pid} 1 1"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie jstat: {output}")
    lines = output.splitlines()
    if len(lines) < 2:
        print("UNKNOWN - Résultat invalide de jstat")
        sys.exit(3)
    
    header = lines[0].split()
    values = lines[1].split()
    try:
        oc_index = header.index("OC")
        ou_index = header.index("OU")
        oc = float(values[oc_index])
        ou = float(values[ou_index])
        ratio = (ou/oc) * 100.0 if oc != 0 else 0.0
    except Exception:
        print("UNKNOWN - Erreur lors de l'analyse de la sortie jstat")
        sys.exit(3)
    
    status = 0
    status_text = "OK"
    if ratio >= critical:
        status = 2
        status_text = "CRITICAL"
    elif ratio >= warning:
        status = 1
        status_text = "WARNING"
    
    if output_mode == "short":
        result = f"{status_text} - GC Old: {ratio:.2f}%"
    else:
        result = (f"{status_text} - GC Old Generation usage: {ratio:.2f}% | "
                  f"thresholds: warning={warning}%, critical={critical}% | "
                  f"performance data: gc_old_usage={ratio:.2f}%;{warning};{critical}")
    print(result)
    sys.exit(status)

def check_heap(ssh, pid, output_mode, debug):
    """
    Affiche la taille du Heap et la mémoire utilisée.
    On utilise 'jstat -gccapacity' pour récupérer les informations.
    Le Heap est estimé par la somme des espaces : S0C, S1C, Eden (E) et Old (O).
    """
    command = f"jstat -gccapacity {pid} 1 1"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie jstat -gccapacity: {output}")
    lines = output.splitlines()
    if len(lines) < 2:
        print("UNKNOWN - Résultat invalide de jstat -gccapacity")
        sys.exit(3)
    header = lines[0].split()
    values = lines[1].split()
    try:
        s0c = float(values[header.index("S0C")])
        s1c = float(values[header.index("S1C")])
        e = float(values[header.index("E")])
        o = float(values[header.index("O")])
        s0u = float(values[header.index("S0U")])
        s1u = float(values[header.index("S1U")])
        eu = float(values[header.index("EU")])
        ou = float(values[header.index("OU")])
        capacity = s0c + s1c + e + o
        used = s0u + s1u + eu + ou
        usage_percent = (used / capacity * 100.0) if capacity != 0 else 0.0
    except Exception as ex:
        if debug:
            print(f"[DEBUG] Exception: {ex}")
        print("UNKNOWN - Erreur lors de l'analyse de la sortie de jstat -gccapacity")
        sys.exit(3)
    if output_mode == "short":
        result = f"HEAP - Used: {used:.0f}, Capacity: {capacity:.0f} ({usage_percent:.1f}%)"
    else:
        result = (f"HEAP usage details:\n"
                  f"  - Used Memory: {used:.0f} units\n"
                  f"  - Heap Capacity: {capacity:.0f} units\n"
                  f"  - Usage: {usage_percent:.1f}% of total heap capacity")
    print(result)
    sys.exit(0)

def check_classes(ssh, pid, output_mode, debug):
    """
    Affiche le nombre de classes chargées.
    On utilise 'jstat -class' pour récupérer ces informations.
    """
    command = f"jstat -class {pid} 1 1"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie jstat -class: {output}")
    lines = output.splitlines()
    if len(lines) < 2:
        print("UNKNOWN - Résultat invalide de jstat -class")
        sys.exit(3)
    header = lines[0].split()
    values = lines[1].split()
    try:
        # On suppose que la première colonne correspond au nombre de classes chargées.
        loaded_classes = int(values[0])
    except Exception as ex:
        if debug:
            print(f"[DEBUG] Exception: {ex}")
        print("UNKNOWN - Erreur lors de l'analyse de la sortie de jstat -class")
        sys.exit(3)
    if output_mode == "short":
        result = f"CLASSES - Loaded: {loaded_classes}"
    else:
        result = f"Number of loaded classes: {loaded_classes} classes are currently loaded in the JVM."
    print(result)
    sys.exit(0)

def check_threads(ssh, pid, output_mode, debug):
    """
    Affiche le nombre de threads actifs pour le processus Java.
    Utilise 'ps -p <pid> -L --no-headers' pour lister tous les threads.
    """
    command = f"ps -p {pid} -L --no-headers"
    if debug:
        print(f"[DEBUG] Exécution de la commande: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    if debug:
        print(f"[DEBUG] Sortie ps -L: {output}")
    # Chaque ligne correspond à un thread
    thread_count = len(output.splitlines())
    if output_mode == "short":
        result = f"THREADS - Active: {thread_count}"
    else:
        result = f"Active Threads: There are {thread_count} threads running in the JVM process."
    print(result)
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description=("Script de monitoring Nagios pour JVM (Tomcat/Catalina ou autre JVM).\n"
                     "Ce script se connecte via SSH pour interroger plusieurs métriques :\n"
                     " - CPU, RAM, Garbage Collector\n"
                     " - Heap (taille et utilisation)\n"
                     " - Nombre de classes chargées\n"
                     " - Nombre de threads actifs"),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-H", "--host", required=True, help="Hôte à interroger")
    parser.add_argument("-i", "--identity", required=True, help="Chemin vers la clé SSH")
    parser.add_argument("-m", "--mode", required=True,
                        choices=["cpu", "ram", "gc", "heap", "classes", "threads"],
                        help=("Mode de vérification :\n"
                              "  cpu     : Vérification de l'utilisation CPU\n"
                              "  ram     : Vérification de l'utilisation RAM\n"
                              "  gc      : Vérification de l'état du Garbage Collector\n"
                              "  heap    : Affichage de la taille et de l'utilisation du Heap\n"
                              "  classes : Affichage du nombre de classes chargées\n"
                              "  threads : Affichage du nombre de threads actifs"))
    parser.add_argument("-w", "--warning", type=float, default=80.0, help="Seuil warning (par défaut 80)")
    parser.add_argument("-c", "--critical", type=float, default=90.0, help="Seuil critical (par défaut 90)")
    parser.add_argument("-u", "--user", default="root", help="Utilisateur SSH (par défaut 'root')")
    parser.add_argument("--debug", action="store_true", help="Active le mode débug (sortie verbeuse)")
    parser.add_argument("--output", choices=["short", "long"], default="short",
                        help="Type de sortie : 'short' pour un résultat court, 'long' pour un résultat détaillé")
    args = parser.parse_args()

    if args.debug:
        print(f"[DEBUG] Tentative de connexion à {args.host} en tant que {args.user} avec la clé {args.identity}")

    # Connexion SSH
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(args.host, username=args.user, key_filename=args.identity)
        if args.debug:
            print(f"[DEBUG] Connexion SSH établie avec succès sur {args.host}")
    except Exception as e:
        print(f"UNKNOWN - Erreur de connexion SSH: {e}")
        sys.exit(3)

    # Récupérer le PID du processus Java
    pid = get_jvm_pid(ssh, args.debug)
    if args.debug:
        print(f"[DEBUG] Processus Java trouvé: PID = {pid}")

    # Lancer le mode de vérification choisi
    if args.mode == "cpu":
        check_cpu(ssh, pid, args.warning, args.critical, args.output, args.debug)
    elif args.mode == "ram":
        check_ram(ssh, pid, args.warning, args.critical, args.output, args.debug)
    elif args.mode == "gc":
        check_gc(ssh, pid, args.warning, args.critical, args.output, args.debug)
    elif args.mode == "heap":
        check_heap(ssh, pid, args.output, args.debug)
    elif args.mode == "classes":
        check_classes(ssh, pid, args.output, args.debug)
    elif args.mode == "threads":
        check_threads(ssh, pid, args.output, args.debug)

if __name__ == "__main__":
    main()
