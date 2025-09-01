"""
Sistema de logging centralizado usando icecream
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from icecream import ic, install
from typing import Any, Optional

# Níveis de logging
LOG_LEVELS = {
    'debug': 0,
    'info': 1,
    'warning': 2,
    'error': 3
}

# Configuração do icecream
ic.configureOutput(
    prefix='📚 Catalog Builder | ',
    includeContext=False,
    outputFunction=lambda *args: print(*args, flush=True)
)

# Instala o icecream como função global
install()

class Logger:
    """Classe para logging centralizado com icecream"""
    
    def __init__(self, name: str = "CatalogBuilder"):
        self.name = name
        self.log_file = None
        self.log_level = self._get_log_level()
        self._setup_log_file()
    
    def _get_log_level(self) -> int:
        """Obtém nível de logging das variáveis de ambiente"""
        log_level_str = os.getenv('LOG_LEVEL', 'info').lower()
        return LOG_LEVELS.get(log_level_str, LOG_LEVELS['info'])
    
    def _should_log(self, level: str) -> bool:
        """Verifica se deve fazer log baseado no nível"""
        return LOG_LEVELS.get(level, LOG_LEVELS['info']) >= self.log_level
    
    def _setup_log_file(self):
        """Configura arquivo de log"""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = log_dir / f"catalog_builder_{timestamp}.log"
            
            # Configura icecream para também escrever no arquivo
            def log_to_file(*args):
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message = ' '.join(str(arg) for arg in args)
                    f.write(f"[{timestamp}] {message}\n")
                print(*args, flush=True)
            
            ic.configureOutput(outputFunction=log_to_file)
            
        except Exception as e:
            print(f"⚠️  Erro ao configurar arquivo de log: {e}")
    
    def info(self, message: str, **kwargs):
        """Log de informação"""
        if self._should_log('info'):
            ic(f"ℹ️  {message}", **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log de sucesso (nível info)"""
        if self._should_log('info'):
            ic(f"✅ {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso"""
        if self._should_log('warning'):
            ic(f"⚠️  {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro"""
        if self._should_log('error'):
            ic(f"❌ {message}", **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        if self._should_log('debug'):
            ic(f"🔍 {message}", **kwargs)
    
    def progress(self, message: str, **kwargs):
        """Log de progresso (nível info)"""
        if self._should_log('info'):
            ic(f"🔄 {message}", **kwargs)
    
    def step(self, step: int, total: int, message: str, **kwargs):
        """Log de etapa com progresso (nível info)"""
        if self._should_log('info'):
            ic(f"📋 [{step}/{total}] {message}", **kwargs)
    
    def section(self, title: str):
        """Log de seção (nível info)"""
        if self._should_log('info'):
            ic(f"\n{'='*50}")
            ic(f"🎯 {title}")
            ic(f"{'='*50}")
    
    def config(self, key: str, value: Any):
        """Log de configuração (nível info)"""
        if self._should_log('info'):
            ic(f"⚙️  {key}: {value}")
    
    def stats(self, stats_dict: dict):
        """Log de estatísticas (nível info)"""
        if self._should_log('info'):
            ic("📊 Estatísticas:")
            for key, value in stats_dict.items():
                ic(f"   {key}: {value}")
    
    def data(self, data: Any, label: str = "Data"):
        """Log de dados (nível debug)"""
        if self._should_log('debug'):
            ic(f"📄 {label}:", data)
    
    def exception(self, message: str, exception: Exception):
        """Log de exceção (nível error)"""
        if self._should_log('error'):
            ic(f"💥 {message}: {exception}")
            ic(f"   Tipo: {type(exception).__name__}")
            if hasattr(exception, '__traceback__'):
                import traceback
                ic(f"   Traceback: {traceback.format_exc()}")

# Instância global do logger
logger = Logger()

# Funções de conveniência
def info(message: str, **kwargs):
    """Log de informação"""
    logger.info(message, **kwargs)

def success(message: str, **kwargs):
    """Log de sucesso"""
    logger.success(message, **kwargs)

def warning(message: str, **kwargs):
    """Log de aviso"""
    logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log de erro"""
    logger.error(message, **kwargs)

def debug(message: str, **kwargs):
    """Log de debug"""
    logger.debug(message, **kwargs)

def progress(message: str, **kwargs):
    """Log de progresso"""
    logger.progress(message, **kwargs)

def step(step: int, total: int, message: str, **kwargs):
    """Log de etapa com progresso"""
    logger.step(step, total, message, **kwargs)

def section(title: str):
    """Log de seção"""
    logger.section(title)

def config(key: str, value: Any):
    """Log de configuração"""
    logger.config(key, value)

def stats(stats_dict: dict):
    """Log de estatísticas"""
    logger.stats(stats_dict)

def data(data: Any, label: str = "Data"):
    """Log de dados"""
    logger.data(data, label)

def exception(message: str, exception: Exception):
    """Log de exceção"""
    logger.exception(message, exception)
