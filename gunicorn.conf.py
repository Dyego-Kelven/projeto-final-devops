import multiprocessing
import os


bind = os.getenv("BIND", "0.0.0.0:8000")
worker_class = "uvicorn.workers.UvicornWorker"

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv("WEB_THREADS", "1"))

timeout = int(os.getenv("WEB_TIMEOUT", "60"))
graceful_timeout = int(os.getenv("WEB_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("WEB_KEEPALIVE", "2"))

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
capture_output = True
