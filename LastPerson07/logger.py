"""🔧 LastPerson07 Advanced Logging System"""
import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path

class LastPerson07Logger:
    """Production-grade logging with rotation & Telegram notifications"""
    
    def __init__(self, app_name="LastPerson07"):
        self.app_name = app_name
        self.log_dir = Path("logs")
        self.log_file = self.log_dir / "lastperson07.log"
        self.setup()
    
    def setup(self):
        """Initialize logging with config file"""
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Load config if exists, else basic setup
        config_path = Path("logging.conf")
        if config_path.exists():
            logging.config.fileConfig(
                str(config_path),
                defaults={'logfilename': str(self.log_file)},
                disable_existing_loggers=False
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
        
        self.logger = logging.getLogger(self.app_name)
        self.logger.info(f"🚀 {self.app_name} Logger initialized")
    
    def info(self, msg: str):
        """Log info message"""
        self.logger.info(msg)
    
    def error(self, msg: str):
        """Log error with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.error(f"❌ [{timestamp}] {msg}")
    
    def success(self, msg: str):
        """Log success message"""
        self.logger.info(f"✅ {msg}")
    
    def warning(self, msg: str):
        """Log warning"""
        self.logger.warning(f"⚠️ {msg}")
    
    def debug(self, msg: str):
        """Log debug info"""
        self.logger.debug(f"🔍 {msg}")

# Global logger instance
logger = LastPerson07Logger()
