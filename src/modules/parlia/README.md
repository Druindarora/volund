# 🎙️ Parlia – Module de transcription vocale pour Vølund

**Parlia** est le module dédié à la reconnaissance vocale dans l’environnement Vølund.  
Il permet de **dicter du texte à la voix**, de le **transcrire automatiquement** à l’aide de modèles IA locaux (Whisper), puis de l’**enrichir** via une interface textuelle évoluée, avant de le **réutiliser** dans différents contextes.

---

## 🧠 Objectif principal

> Permettre à l'utilisateur de **parler librement**, puis d'agir sur le texte dicté : édition, formatage, export, interaction avec d'autres modules (dev, messagerie, mémoire...).

---

## 🗂️ Structure du module

voice/
├── services/ # Gestion de la reconnaissance vocale, modèles, état
├── ui/ # Composants graphiques : zone de texte, boutons, paramètres
├── db/ # (optionnel) Historique des dictées, configurations utilisateur
├── tests/ # Tests unitaires du module
├── assets/ # Ressources visuelles (icônes, sons, etc.)
├── init.py # Métadonnées + fonction launch(parent)
└── README.md # Ce fichier


---

## ⚙️ Fonctionnalités prévues

- 🎙️ **Transcription vocale locale (Whisper)**
  - Choix dynamique du modèle
  - Affichage de l’état (chargé / en cours)
  - Démarrage / arrêt par bouton ou raccourci

- 📝 **Zone de texte enrichie**
  - Mise en forme (gras, emojis, couleurs...)
  - Ajout de commandes prédéfinies (ex. pour Copilot, reformulation, etc.)
  - Export vers d'autres apps/modules

- 🧩 **Boutons d’action modulaires**
  - Groupés par catégorie : dictée, texte, export
  - Reconfigurables (bientôt via keymap.json ?)

- 🔄 **Navigation fluide**
  - Intégration complète avec la home et la sidebar Vølund
  - Module autonome mais interconnecté

---

## 🛣️ Prochaines étapes

- [x] Génération automatique via `GenerateModule`
- [ ] Activation de la navigation (carte Parlia ↔ sidebar ↔ accueil)
- [ ] Création de la page d’accueil Parlia (`createVoiceHome`)
- [ ] Intégration Whisper (gestion des modèles)
- [ ] Zone de texte riche + boutons dynamiques

---

## 🧪 Notes de développement

- Le module est pensé pour évoluer :
  - Ajout futur d’une **commande vocale**
  - Historique des messages transcrits
  - Intégration avec MemoQuiz pour transformer une dictée en carte mémoire
- Aucune dépendance cloud : tout est local
- L’utilisateur contrôle chaque étape de l’enregistrement → pas d’automatisation cachée

---

> **Statut actuel** : 🟡 _En développement initial (UI + navigation)_

---

