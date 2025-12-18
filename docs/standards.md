# Standards de Code et d'Expérimentation ML

## Standards de Code
- Commits : Conventional commits (feat:/fix:/docs: etc.) pour traçabilité.
- Formatting/Linting : Black pour format, Flake8 pour lint (via CI).
- Dépendances : Poetry pour lock/reproductibilité.
- Tests : Pytest avec cov >80%, couvrant cas critiques/erreurs.

## Standards d'Expérimentation ML
- Datasets : Utiliser P3/P4 pour tests unitaires/fonctionnels.
- Traçabilité : Log inputs/outputs en DB PostgreSQL.
- Validation : Pydantic pour inputs API ; tester performances/limites.
- CI/CD : Tests auto sur push ; environnements dev (local/tests) / prod (HF main).