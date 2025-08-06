# Network binding
bind = "0.0.0.0:8000"

# Worker settings
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 60
graceful_timeout = 30
keepalive = 5
