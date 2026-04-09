## Tests unitaires (devis_app)

Ce projet contient des tests unitaires pour l'application `devis_app`.

### Procédure pour exécuter les tests

1. Ouvrir un terminal dans le dossier du projet.
2. Activer l'environnement virtuel si besoin :
   
  ```powershell
  .\env\Scripts\activate
  ```
  ou
  ```bash
  source env/bin/activate
  ```
3. Lancer la commande suivante :
   
  ```bash
  python manage.py test devis_app -v 2
  ```

### Résultat attendu

Tous les tests doivent passer sans erreur (`OK`).

---
*Documenté le 29/11/2025 par [Traore Husseni ]*
# Projet_Devis
  - devis
  - Devis2025

  -pwa 
  pwa 2026

## CI/CD Auto Deploy (Push -> Validation -> Servers)

Le projet est configuré avec GitHub Actions dans `.github/workflows/ci-cd.yml`.

Flux:
1. Push sur `main`.
2. Validation automatique: `python manage.py check` + `python manage.py test devis_app -v 2`.
3. Si validation OK, déploiement automatique sur les 2 serveurs avec `scripts/deploy_docker.sh`.

Secrets GitHub requis (Repository -> Settings -> Secrets and variables -> Actions):
- `SSH_PRIVATE_KEY`: clé privée SSH utilisée par GitHub Actions.
- `SERVER_A_HOST`: IP/Domaine du serveur site A.
- `SERVER_A_PORT`: port SSH (souvent `22`).
- `SERVER_A_USER`: utilisateur SSH du serveur site A.
- `SERVER_B_HOST`: IP/Domaine du serveur site B.
- `SERVER_B_PORT`: port SSH (souvent `22`).
- `SERVER_B_USER`: utilisateur SSH du serveur site B.

Pré-requis serveurs:
- La clé publique associée à `SSH_PRIVATE_KEY` doit être dans `~/.ssh/authorized_keys` de chaque serveur.
- Le script `/var/www/devis/Pwa/scripts/deploy_docker.sh` doit être exécutable.
- L'utilisateur SSH doit pouvoir exécuter Docker Compose sans prompt interactif.



