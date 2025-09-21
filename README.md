// README.md — Guide pour un serveur local React + Node

# Projet : Application de Simulation de Scope Médical

## Objectif

Créer une application web ultra-accessible pour un enseignant non développeur. Elle doit fonctionner localement sans Internet, sur tous les systèmes, et gérer intelligemment les éventuels problèmes de port ou réseau. L'interface simule de manière réaliste un scope médical utilisé dans les établissements de santé français pour la formation des étudiants en soins infirmiers et médecine.

## Stack Technologique

- **Frontend** : React 19.1.0 avec TypeScript
- **Graphiques** : Recharts 2.15.3 pour les tracés physiologiques
- **Build** : Vite 6.2.0
- **Styling** : CSS-in-JS avec classes Tailwind
- **Interface** : Simulation fidèle d'un scope utilisé dans les établissements de santé français

## Structure du Projet

```
simu-scope/
├── src/
│   ├── App.tsx                    # Composant principal avec gestion des scénarios
│   ├── components/
│   │   └── scope/
│   │       ├── ScopeDisplay.tsx   # Affichage principal du scope
│   │       ├── VitalsDisplay.tsx  # Paramètres vitaux numériques
│   │       └── WaveformTrace.tsx  # Tracés physiologiques (ECG, Pleth, Resp)
│   ├── assets/
│   │   └── icons/
│   │       └── HeartIcon.tsx      # Icône cœur pour l'interface
│   ├── constants/
│   │   ├── scenarios.ts           # Scénarios médicaux prédéfinis
│   │   └── index.ts              # Patterns de signaux
│   └── types/
│       └── index.ts              # Définitions TypeScript
├── package.json                  # Dépendances et scripts
├── vite.config.ts               # Configuration Vite
└── tsconfig.json                # Configuration TypeScript
```

## Fonctionnement Actuel

1. **Développement** : `npm run dev` pour lancer le serveur de développement Vite
2. **Build** : `npm run build` pour créer la version de production
3. **Contrôles** :
   - Touches 1-5 : Changer de scénario médical
   - Touche H : Afficher/masquer l'aide professeur

## Fonctionnement Futur (Architecture Serveur)

1. L'utilisateur double-clique sur un script (Windows: `start.bat`, Mac/Linux: `start.sh`)
2. Le script :
   - Cherche un port disponible (par ex. 3000 → 3001 → ...)
   - Vérifie que l'IP locale est accessible sur le réseau
   - Lance le serveur Node.js local
   - Ouvre automatiquement l'interface dans un navigateur (sur l'IP locale si disponible)
3. Le téléphone accède à l'interface via l'IP locale (ex: `http://192.168.1.12:3000`)

## Fonctionnalités Implémentées ✅

### Interface Utilisateur
- **Design réaliste** : Interface reproduisant fidèlement un scope médical français
- **Layout responsive** : Optimisé pour tablettes et smartphones  
- **Thème médical** : Couleurs et typographie conformes aux standards hospitaliers

### Tracés Physiologiques
- **ECG (Électrocardiogramme)** : Tracé en temps réel en vert clair
- **Plethysmographie (SpO₂)** : Courbe de saturation en cyan
- **Respiration (FR)** : Tracé respiratoire en jaune
- **Rendu fluide** : 50 échantillons/seconde pour des tracés lisses
- **Adaptation dynamique** : Les patterns s'adaptent automatiquement aux valeurs

### Contrôle à Distance
- **Interface mobile** : Contrôle depuis téléphone/tablette
- **Transitions réalistes** : Les valeurs changent progressivement (FC: 2 bpm/s, SpO₂: 1%/s, FR: 1/min/s)
- **Affichage dual** : Valeur actuelle et valeur cible affichées
- **Communication temps réel** : WebSocket pour synchronisation instantanée
- **QR Code** : Accès rapide à l'interface mobile

### Paramètres Vitaux Contrôlables
- **FC (Fréquence Cardiaque)** : 0-300 bpm, couleur vert clair
- **SpO₂ (Saturation)** : 0-100%, couleur cyan
- **FR (Fréquence Respiratoire)** : 0-60 /min, couleur jaune
- **PNI (Pression Non Invasive)** : Affichage statique

## Installation et Lancement

### ⚡ Lancement IMMÉDIAT (Aucun prérequis)

**Windows :**
```bat
double-clic sur DEMARRAGE-IMMEDIAT.bat
```
**Aucune installation requise - Fonctionne sur n'importe quel ordinateur !**

### 🌐 Lancement Réseau (Contrôle multi-appareils)

**Windows :**
```bat
double-clic sur start.bat
```

**Mac/Linux :**
```bash
./start.sh
```
**Requis : Node.js (pour compilation) + Python (pour serveur)**

### 📱 Utilisation

#### Version Immédiate (1 appareil)
1. **Double-clic** sur `DEMARRAGE-IMMEDIAT.bat`
2. **Interface scope** : S'ouvre automatiquement
3. **Contrôle** : Cliquez "Interface de Contrôle" pour modifier les valeurs
4. **Transitions** : Retournez au scope pour voir les changements réalistes

#### Version Réseau (multi-appareils)
1. **Interface principale** : S'ouvre automatiquement dans le navigateur
2. **Interface mobile** : Scannez le QR Code affiché dans le terminal
3. **Contrôle** : 
   - Entrez les nouvelles valeurs sur le téléphone
   - Les courbes changent en temps réel sur l'écran principal
   - Transitions progressives et réalistes

### 🛠️ Développement

```bash
# Développement avec hot reload
python server.py

# Compilation vers exécutable autonome (.exe)
python build_executable.py

# Test de l'exécutable
cd dist
SimulateurScope.exe
```

### 📦 Commandes de Build

```bash
# Installer PyInstaller (une seule fois)
pip install pyinstaller

# Créer l'exécutable autonome
python build_executable.py

# Exécutable généré dans : dist/SimulateurScope.exe
# Taille : ~8 MB
# Fonctionne sans Python installé
```

## Étapes de Développement Futures

### 1. Création du backend Express

```bash
mkdir backend
cd backend
npm init -y
npm install express detect-port local-ip-url open
```

### 2. Serveur Express intelligent (backend/index.js)

```js
const express = require("express");
const path = require("path");
const detect = require("detect-port");
const ip = require("local-ip-url");
const open = require("open");

const app = express();
const DEFAULT_PORT = 3000;

(async () => {
  const port = await detect(DEFAULT_PORT);
  const localAddress = ip("public", "ipv4");

  // Servir les fichiers React compilés (dist avec Vite)
  app.use(express.static(path.join(__dirname, "../dist")));

  app.get("*", (req, res) => {
    res.sendFile(path.join(__dirname, "../dist/index.html"));
  });

  app.listen(port, () => {
    const url = `http://${localAddress}:${port}`;
    console.log(`App running at ${url}`);
    open(url).catch(() => {
      console.log("Veuillez ouvrir manuellement l'URL:", url);
    });
  });
})();
```

### 3. Script de démarrage (Windows — `start.bat`)

```bat
@echo off
echo Compilation du frontend...
call npm run build
echo Lancement du serveur...
cd backend
call npm install
node index.js
```

### 4. Accès depuis un autre appareil sur le réseau

- Trouver l'IP locale automatiquement grâce au script
- Affichage dans le terminal et ouverture automatique dans le navigateur
- Génération automatique d'un QR Code avec l'IP pour accès mobile rapide

## État Actuel du Projet

Le projet est **pleinement fonctionnel** avec toutes les fonctionnalités principales implémentées :
- ✅ Interface scope réaliste
- ✅ Tracés physiologiques fluides et adaptatifs
- ✅ Contrôle à distance par téléphone
- ✅ Serveur local avec WebSocket
- ✅ Scripts de démarrage automatisés
- ✅ Transitions réalistes entre valeurs
- ✅ QR Code pour accès mobile rapide

## Fonctionnalités Avancées Possibles

1. **Alarmes sonores** : Sons d'alerte pour valeurs critiques
2. **Historique** : Sauvegarde des sessions et replay
3. **Personnalisation** : Création de patterns personnalisés
4. **Multi-patients** : Gestion de plusieurs scopes simultanés

## Utilisation en Salle de Classe

### Configuration Recommandée
1. **Ordinateur professeur** : Lance `start.bat` ou `start.sh`
2. **Écran/Projecteur** : Affiche l'interface scope réaliste
3. **Téléphone professeur** : Contrôle discret des paramètres
4. **Réseau local** : Tous les appareils sur le même WiFi

### Avantages Pédagogiques
- **Réalisme** : Interface identique aux vrais scopes hospitaliers
- **Flexibilité** : Changement instantané des paramètres vitaux
- **Engagement** : Simulations interactives et évolutives
- **Simplicité** : Aucune configuration technique requise

## Sécurité

- L'application tourne uniquement en local (LAN)
- Aucune donnée sensible stockée ou transmise
- Communication chiffrée WebSocket
- Pas d'accès Internet requis
