Générateur de Factures

Générateur de factures alimenté par l'IA qui extrait des informations à partir d'images et génère des factures PDF professionnelles.

Configuration

1. Créez un fichier .env avec votre clé API Gemini :

GEMINI_API_KEY=votre_clé_api_ici

2. Installez les dépendances :

uv pip install -r pyproject.toml

3. Exécutez l'application :

streamlit run frontend/app.py

Utilisation

1. Ouvrez l'application dans votre navigateur
2. Téléchargez une image contenant des informations de facture
3. L'IA extraira les données et générera une facture PDF
4. Téléchargez la facture générée
5. L'historique des conversations persiste dans la base de données SQLite



Technologies

- Streamlit : Interface Web
- LiteLLM : Intégration de l'IA Gemini
- ReportLab : Génération de PDF
- SQLite : Persistance de l'historique des conversations
