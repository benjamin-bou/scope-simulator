// README.md — Guide pour un serveur local React + Node

# Projet : Application de Simulation de Scope Médical

## Objectif

Créer une application web ultra-accessible pour un enseignant non développeur. Elle doit fonctionner localement sans Internet, sur tous les systèmes, et gérer intelligemment les éventuels problèmes de port ou réseau. L'interface simule de manière réaliste un scope médical utilisé dans les établissements de santé français pour la formation des étudiants en soins infirmiers et médecine.

## Stack Technologique

- **Frontend** : React avec design réaliste de scope médical français
- **Backend** : Node.js avec Express
- **Communication Réseau** : WebSocket ou API REST (selon besoin)
- **Interface** : Simulation fidèle d'un scope utilisé dans les établissements de santé français

## Fonctionnement

1. L'utilisateur double-clique sur un script (Windows: `start.bat`, Mac/Linux: `start.sh`)
2. Le script :
   - Cherche un port disponible (par ex. 3000 → 3001 → ...)
   - Vérifie que l'IP locale est accessible sur le réseau
   - Lance le serveur Node.js local
   - Ouvre automatiquement l'interface dans un navigateur (sur l'IP locale si disponible)
3. Le téléphone accède à l'interface via l'IP locale (ex: `http://192.168.1.12:3000`)

## Étapes de Développement

### 1. Initialiser le projet

```bash
npx create-react-app frontend
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

  // Servir les fichiers React compilés
  app.use(express.static(path.join(__dirname, "../frontend/build")));

  app.get("*", (req, res) => {
    res.sendFile(path.join(__dirname, "../frontend/build/index.html"));
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
cd backend
call npm install
node index.js
```

### 4. Développement de l'interface scope réaliste

**Design du frontend :**
- Interface reproduisant fidèlement un scope médical français
- Écrans et boutons conformes aux standards hospitaliers français
- Affichage des paramètres vitaux (fréquence cardiaque, tension, saturation, etc.)
- Design responsive optimisé pour tablettes et smartphones
- Couleurs et typographie respectant les codes visuels médicaux

**Compilation du frontend React :**

```bash
cd frontend
npm run build
```

### 5. Accès depuis un autre appareil sur le réseau

- Trouver l'IP locale automatiquement grâce au script
- Affichage dans le terminal et ouverture automatique dans le navigateur

## Astuces

- **QR Code** : Générer automatiquement un QR Code avec l'IP pour un accès rapide depuis mobile
- **Réservation IP** : Configurer la box pour réserver l'adresse IP de l'ordinateur
- **Design médical** : Respecter les standards visuels des équipements médicaux français
- **Simulation réaliste** : Interface identique aux scopes Philips, GE Healthcare ou Mindray utilisés en France

## Robustesse & Accessibilité

- Le port est automatiquement trouvé (3000, 3001, etc.)
- Le serveur s'ouvre automatiquement dans le navigateur
- Fonctionne sur tout type de réseau ou configuration
- Aucun besoin de compétence technique pour l'utilisateur
- Interface intuitive reproduisant l'ergonomie des équipements médicaux réels

## Sécurité

- L'application tourne uniquement en local (LAN)
- Ne pas exposer les ports manuellement sans protection

---

Ce guide peut être utilisé comme base pour générer automatiquement toute l'architecture du projet avec un script ou une IA spécialisée.
