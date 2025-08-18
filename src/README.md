# Structure du code source

## Organisation des dossiers

```
src/
├── App.tsx                 # Composant racine de l'application
├── types/                  # Définitions TypeScript
│   └── index.ts           # Types principaux (Scenario, etc.)
├── constants/             # Constantes de l'application
│   ├── scenarios.ts       # Définitions des scénarios médicaux et patterns
│   └── index.ts          # Re-exports des constantes
├── components/           # Composants React
│   ├── scope/            # Composants spécifiques au scope médical
│   │   ├── ScopeDisplay.tsx      # Layout principal du scope
│   │   ├── VitalsDisplay.tsx     # Affichage des paramètres vitaux
│   │   ├── WaveformTrace.tsx     # Tracés physiologiques (ECG, Pleth, Resp)
│   │   └── index.ts             # Re-exports des composants scope
│   └── ui/               # Composants UI génériques (vide actuellement)
├── assets/               # Ressources statiques
│   └── icons/           # Icônes SVG
│       ├── HeartIcon.tsx # Icône de cœur pour l'interface
│       └── index.ts     # Re-exports des icônes
├── hooks/                # Hooks React personnalisés (vide actuellement)
└── utils/                # Fonctions utilitaires (vide actuellement)
```

## Bonnes pratiques appliquées

### 1. Séparation des responsabilités
- **components/scope/** : Composants métier spécifiques au domaine médical
- **components/ui/** : Composants UI réutilisables
- **types/** : Définitions TypeScript centralisées
- **constants/** : Constantes et configuration

### 2. Organisation modulaire
- Chaque dossier a un fichier `index.ts` pour faciliter les imports
- Structure hiérarchique claire avec séparation logique
- Re-exports organisés pour éviter les imports profonds

### 3. Conventions de nommage
- **PascalCase** pour les composants React
- **camelCase** pour les fichiers utilitaires
- **kebab-case** évité au profit de camelCase/PascalCase

### 4. Imports optimisés
```typescript
// ✅ Bon : import depuis le barrel
import { ScopeDisplay, VitalsDisplay } from './components/scope';
import { SCENARIOS } from './constants';
import type { Scenario } from './types';

// ❌ Évité : imports profonds
import { ScopeDisplay } from './components/scope/ScopeDisplay';
import { VitalsDisplay } from './components/scope/VitalsDisplay';
```

### 5. Structure évolutive
- Dossiers `hooks/` et `utils/` prêts pour de futures fonctionnalités
- Séparation claire entre composants métier et UI génériques
- Architecture modulaire permettant l'ajout facile de nouvelles fonctionnalités