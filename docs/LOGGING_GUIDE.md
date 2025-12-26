# 🎯 Guide de Logging - Employee Turnover API

## 📋 Vue d'ensemble

Le système de logging utilise **python-json-logger** pour produire des logs structurés en JSON, facilitant l'analyse et l'intégration avec des outils de monitoring.

## 📁 Structure des logs

```
logs/
├── api.log       # Tous les logs (INFO, WARNING, ERROR)
└── error.log     # Erreurs uniquement (ERROR, CRITICAL)
```

## 🔧 Configuration

### Fichier .env
```bash
# Niveau de log : DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# En mode DEBUG, logs console en format texte
DEBUG=true
```

### Niveaux de log

| Niveau | Usage | Exemple |
|--------|-------|---------|
| **DEBUG** | Détails techniques | Variables, états internes |
| **INFO** | Événements normaux | Requêtes, prédictions |
| **WARNING** | Situations anormales non-bloquantes | 404, validation errors |
| **ERROR** | Erreurs nécessitant attention | 500, exceptions |
| **CRITICAL** | Défaillances système | Modèle indisponible |

## 📊 Formats de logs

### Log de requête
```json
{
  "timestamp": "2025-12-26T10:30:45.123456",
  "level": "INFO",
  "logger": "employee_turnover_api",
  "module": "app",
  "function": "log_requests",
  "line": 67,
  "message": "Request POST /predict",
  "method": "POST",
  "path": "/predict",
  "status_code": 200,
  "duration_ms": 23.45,
  "client_host": "127.0.0.1"
}
```

### Log de prédiction
```json
{
  "timestamp": "2025-12-26T10:30:45.234567",
  "level": "INFO",
  "message": "Prediction made",
  "employee_id": null,
  "prediction": 0,
  "probability": 0.1523,
  "risk_level": "Low",
  "duration_ms": 18.32
}
```

### Log d'erreur
```json
{
  "timestamp": "2025-12-26T10:30:45.345678",
  "level": "ERROR",
  "message": "Unexpected error during prediction",
  "module": "app",
  "function": "predict",
  "line": 215,
  "exc_info": "Traceback (most recent call last):\n..."
}
```

## 🔍 Utilisation

### Dans le code

```python
from src.logger import logger, log_prediction, log_request

# Log simple
logger.info("Modèle chargé", extra={"version": "2.1.0"})

# Log avec métadonnées
logger.warning("Prédiction lente", extra={
    "duration_ms": 500,
    "employee_id": "EMP123"
})

# Log d'erreur avec exception
try:
    result = risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # Inclut traceback
```

### Fonctions utilitaires

```python
# Logger une requête HTTP
log_request(
    method="POST",
    path="/predict",
    status_code=200,
    duration_ms=23.45,
    user_id="user123"  # Métadonnées custom
)

# Logger une prédiction
log_prediction(
    employee_id="EMP123",
    prediction=1,
    probability=0.87,
    risk_level="high",
    duration_ms=18.5
)

# Logger chargement du modèle
log_model_load(
    model_type="XGBoost Pipeline",
    duration_ms=1234.5,
    success=True
)
```

## 📈 Analyse des logs

### Commandes bash

```bash
# Suivre les logs en temps réel
tail -f logs/api.log

# Filtrer par niveau
cat logs/api.log | jq 'select(.level=="ERROR")'

# Requêtes les plus lentes
cat logs/api.log | jq 'select(.path=="/predict") | .duration_ms' | sort -n | tail -10

# Nombre d'erreurs par endpoint
cat logs/error.log | jq -r '.path' | sort | uniq -c

# Prédictions par risk level
cat logs/api.log | jq 'select(.risk_level != null) | .risk_level' | sort | uniq -c

# Temps moyen de prédiction
cat logs/api.log | jq 'select(.message=="Prediction made") | .duration_ms' | jq -s 'add/length'

# Top 10 IPs
cat logs/api.log | jq -r '.client_host' | sort | uniq -c | sort -rn | head -10
```

### Requêtes jq avancées

```bash
# Erreurs avec contexte
cat logs/error.log | jq '{time: .timestamp, error: .message, module: .module, line: .line}'

# Stats par status code
cat logs/api.log | jq -r 'select(.status_code) | .status_code' | sort | uniq -c

# Prédictions high risk
cat logs/api.log | jq 'select(.risk_level=="high") | {time: .timestamp, prob: .probability}'

# Détection d'anomalies (>1s)
cat logs/api.log | jq 'select(.duration_ms > 1000) | {path: .path, duration: .duration_ms}'
```

## 🎛️ Intégration monitoring

### ELK Stack (Elasticsearch + Logstash + Kibana)

**Logstash config** :
```ruby
input {
  file {
    path => "/app/logs/api.log"
    codec => "json"
    type => "api_logs"
  }
}

filter {
  if [type] == "api_logs" {
    date {
      match => ["timestamp", "ISO8601"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "api-logs-%{+YYYY.MM.dd}"
  }
}
```

### Grafana Loki

**Promtail config** :
```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: api_logs
    static_configs:
      - targets: [localhost]
        labels:
          job: employee_turnover_api
          __path__: /app/logs/api.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            status_code: status_code
```

### CloudWatch (AWS)

```python
import watchtower
import logging

logger = logging.getLogger("employee_turnover_api")
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group="/aws/api/employee-turnover",
    stream_name="production"
))
```

## 🚨 Alertes recommandées

### 1. Taux d'erreur élevé
```
Condition: (errors / total_requests) > 0.05
Action: Email + PagerDuty
```

### 2. Latence élevée
```
Condition: avg(duration_ms) > 500
Action: Slack notification
```

### 3. Rate limiting déclenché
```
Condition: count(status_code==429) > 10
Action: Log alert
```

### 4. Modèle non disponible
```
Condition: log_message contains "Model not available"
Action: Critical alert + SMS
```

## 📝 Best practices

### ✅ À faire

```python
# Logs avec contexte
logger.info("Processing request", extra={
    "user_id": user_id,
    "endpoint": "/predict",
    "payload_size": len(data)
})

# Utiliser les niveaux appropriés
logger.debug("Variable value", extra={"x": x})  # Dev only
logger.info("User action", extra={"action": "predict"})  # Normal
logger.warning("Slow query", extra={"duration": 2.5})  # Attention
logger.error("Failed", exc_info=True)  # Erreur
```

### ❌ À éviter

```python
# Logs sans contexte
logger.info("Error")  # Quoi ? Où ? Pourquoi ?

# Données sensibles
logger.info(f"API Key: {api_key}")  # JAMAIS !

# Logs excessifs en boucle
for item in large_list:
    logger.debug(f"Processing {item}")  # Pollue les logs
```

## 🔐 Sécurité

### Données à masquer
- API Keys
- Tokens d'authentification
- Informations personnelles (PII)
- Mots de passe
- Emails complets

### Exemple de masquage
```python
def mask_sensitive(data):
    if "api_key" in data:
        data["api_key"] = data["api_key"][:8] + "***"
    if "email" in data:
        data["email"] = data["email"].split("@")[0] + "@***"
    return data

logger.info("User data", extra=mask_sensitive(user_data))
```

## 📊 Métriques utiles

### Performance
- `duration_ms` : Temps de traitement
- `status_code` : Codes HTTP
- `model_load_time` : Temps chargement modèle

### Business
- `prediction` : 0 ou 1
- `risk_level` : Low, Medium, High
- `probability` : Probabilité de turnover

### Système
- `level` : Niveau de log
- `client_host` : IP du client
- `path` : Endpoint appelé

## 🔄 Rotation des logs

**Configuration recommandée** :
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/api.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5            # Garder 5 fichiers
)
```

**Avec logrotate** :
```bash
# /etc/logrotate.d/employee-turnover-api
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
}
```

## 📚 Ressources

- [python-json-logger](https://github.com/madzak/python-json-logger)
- [ELK Stack](https://www.elastic.co/elk-stack)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)

---

**Dernière mise à jour** : 26 décembre 2025  
**Version** : 2.1.0
