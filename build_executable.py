#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer un exécutable autonome du simulateur de scope médical
"""

import os
import subprocess
import sys
import shutil
import time

def kill_simulator_processes():
    """Force l'arrêt des processus SimulateurScope"""
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq SimulateurScope.exe"],
                              capture_output=True, text=True)
        if "SimulateurScope.exe" in result.stdout:
            print("Arrêt forcé des processus SimulateurScope en cours...")
            subprocess.run(["taskkill", "/F", "/IM", "SimulateurScope.exe"],
                         capture_output=True)
            time.sleep(2)  # Attendre que les processus se ferment
    except:
        pass

def build_executable():
    """Crée l'exécutable avec PyInstaller"""

    print("=== Build Simulateur Scope Médical ===")
    print()

    # Arrêter les processus en cours
    kill_simulator_processes()

    # Nettoyer les anciens builds
    print("Nettoyage des anciens builds...")
    try:
        if os.path.exists("dist"):
            shutil.rmtree("dist")
    except PermissionError:
        print("Erreur: 'dist' encore verrouillé. Tentative d'arrêt forcé...")
        kill_simulator_processes()
        time.sleep(2)
        try:
            shutil.rmtree("dist")
        except PermissionError:
            print("ERREUR: Impossible de supprimer 'dist'")
            print("Solution: Redémarrer l'ordinateur puis relancer le build")
            return False

    try:
        if os.path.exists("build"):
            shutil.rmtree("build")
    except PermissionError:
        print("Attention: Impossible de supprimer 'build' (continuons quand même)")
        pass

    # Commande PyInstaller
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # Un seul fichier exe
        "--windowed",                   # Sans console
        "--name", "SimulateurScope",    # Nom de l'exe
        "--icon", "NONE",               # Pas d'icône spéciale
        "server.py"                     # Script principal
    ]

    print("Création de l'exécutable...")
    print("Commande:", " ".join(cmd))
    print()

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build réussi!")
        print()

        # Vérifier que l'exe existe
        exe_path = os.path.join("dist", "SimulateurScope.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Fichier créé: {exe_path}")
            print(f"Taille: {size_mb:.1f} MB")
            print()
            print("INSTRUCTIONS POUR L'UTILISATEUR FINAL:")
            print("=====================================")
            print("1. Copiez SimulateurScope.exe sur n'importe quel PC Windows")
            print("2. Double-cliquez sur SimulateurScope.exe")
            print("3. L'application se lance automatiquement dans le navigateur")
            print("4. Utilisez l'URL mobile affichée pour contrôler depuis un téléphone")
            print()
            print("Aucune installation requise - Fonctionne sur n'importe quel Windows!")

        return True

    except subprocess.CalledProcessError as e:
        print("Erreur lors du build:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = build_executable()
    if not success:
        sys.exit(1)