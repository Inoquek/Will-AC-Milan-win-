"""
Configuration management for Serie A Predictor
"""
import os
from dataclasses import dataclass
from typing import List, Optional
import yaml
from pathlib import Path


@dataclass
class ScraperConfig:
    """Configuration for web scraper"""
    base_url: str = "https://www.flashscore.co.uk/football/italy/serie-a-"
    headless: bool = True
    timeout: int = 10
    max_retries: int = 3
    delay_between_requests: float = 2.0
    max_matches_per_season: int = 380
    

@dataclass
class ModelConfig:
    """Configuration for ML models"""
    random_state: int = 42
    test_size: float = 0.2
    validation_size: float = 0.2
    cv_folds: int = 5
    n_estimators: int = 100
    max_depth: Optional[int] = None
    min_samples_split: int = 10
    

@dataclass
class DataConfig:
    """Configuration for data handling"""
    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    external_data_dir: str = "data/external"
    backup_dir: str = "data/backup_data"
    
    # Data quality thresholds
    max_missing_percentage: float = 20.0
    min_matches_per_season: int = 300
    

@dataclass
class Config:
    """Main configuration class"""
    scraper: ScraperConfig
    model: ModelConfig
    data: DataConfig
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                
            return cls(
                scraper=ScraperConfig(**config_dict.get('scraper', {})),
                model=ModelConfig(**config_dict.get('model', {})),
                data=DataConfig(**config_dict.get('data', {}))
            )
        else:
            # Return default configuration
            return cls(
                scraper=ScraperConfig(),
                model=ModelConfig(),
                data=DataConfig()
            )
    
    def to_yaml(self, config_path: str) -> None:
        """Save configuration to YAML file"""
        config_dict = {
            'scraper': self.scraper.__dict__,
            'model': self.model.__dict__,
            'data': self.data.__dict__
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)


# Global configuration instance
_config = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        config_path = os.path.join(Path(__file__).parent.parent.parent, 'config.yaml')
        _config = Config.from_yaml(config_path)
    return _config

def set_config(config: Config) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config
