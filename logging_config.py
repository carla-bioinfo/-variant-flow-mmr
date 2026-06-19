# -*- coding: utf-8 -*-
"""Sistema de logging profissional."""
import logging
from pathlib import Path

class LoggerManager:
    def __init__(self, log_dir="output/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Adicionar handler para MOSTRAR logs no console
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

def get_logger(name):
    return LoggerManager().get_logger(name)

if __name__ == "__main__":
    logger = get_logger("test")
    logger.info("Logging OK")
