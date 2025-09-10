import logging
import os

def get_logger(run_id: str, logs_dir: str = "logs"):
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f"etl_{run_id}.log")

    logger = logging.getLogger(f"etl.{run_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    logger.info(f"Log initialized at {log_path}")
    return logger, log_path
