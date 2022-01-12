import os

bind = "0.0.0.0:8000"

workers = 3
max_requests = 3000
max_requests_jitter = 1000

# staging 环境下，显示 access-log
if os.environ.get("STAGE") != "production":
    accesslog = "-"
    loglevel = "DEBUG"
