# Vølund

## 🚀 Introduction
Vølund est un **outil modulaire pour développeurs**.  
Il permet de **générer automatiquement des modules en Python**, en orchestrant leur création via des modèles d’intelligence artificielle (Whisper, Olama, API OpenAI, etc.).  

Vølund est la **partie développeur** d’un écosystème :  
- côté **développeur** → création, test et packaging de modules.  
- côté **utilisateur** (future app cliente) → utilisation des modules packagés.  

---

## ✨ Fonctionnalités actuelles
- Génération automatisée de modules (dossiers + fichiers standards).  
- Templates avec **Jinja2** (init, logger, UI, tests, README, etc.).  
- Interface graphique **PySide6** pour la création de modules.  
- Première intégration de **Whisper** (transcription vocale → spec).  
- Support de **Olama** comme backend IA (choix de modèles).  

---

## 🛠️ Fonctionnalités prévues
- Bouton **"Generate from spec"** : génération complète de module à partir d’une spec.  
- Split automatique : passage du **monolithe** généré → arborescence micro.  
- Packaging de modules pour distribution.  
- Macro-actions supplémentaires (tests automatisés, validation de spec).  
- Micro-actions (refactor, documentation, génération automatique de tests).  
- Module **TraqIA** : statistiques d’usage (tokens, coûts, volume par période).  

---

## 🏗️ Architecture
- **Langage** : Python 3  
- **UI** : PySide6  
- **Templates** : Jinja2  
- **IA** : Whisper (speech-to-text), Olama (LLM runtime), API OpenAI (optionnel)  
- **Organisation des modules** :  

.
├── assets
├── core
├── db
├── i18n
├── services
├── tests
├── ui
├── utils
├── workers
└── spec



---

## 📦 Installation & lancement
> ⚠️ WIP – instructions d’installation simplifiées, l’outillage complet sera documenté plus tard.

```bash
git clone <repo>
cd volund
pip install -r requirements.txt
python main.py
```

---

##  🧪 Exemple rapide

Créer un module nommé azerty depuis l’UI.
Il apparaît automatiquement dans la liste des modules.
Le home panel du module affiche : Bienvenue dans ce nouveau module.

---

## 🤝 Contribution

Pour l’instant, Vølund est développé en solo.
Standards appliqués :
Fonctions/méthodes en camelCase.
Fichiers en snake_case.
UI basée sur PySide6.

---

## 📜 Licence

Licence libre (probablement MIT, à préciser).


---