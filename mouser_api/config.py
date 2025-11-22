"""
Configurações da API Mouser
"""

import os
from dotenv import load_dotenv

load_dotenv()

class MouserConfig:
    """Configurações da API Mouser"""
    
    # API Key
    API_KEY = os.getenv('MOUSER_API_KEY', 'b6e26deb-732d-4771-9d90-02ea60ca3a21')
    
    # URLs da API
    BASE_URL = "https://api.mouser.com"
    API_VERSION = "v1"
    
    # Endpoints
    SEARCH_BY_PART_NUMBER_URL = f"{BASE_URL}/api/{API_VERSION}/search/partnumber"
    SEARCH_BY_KEYWORD_URL = f"{BASE_URL}/api/{API_VERSION}/search/keyword"
    
    # Limitações da API
    MAX_REQUESTS_PER_MINUTE = 30
    MAX_REQUESTS_PER_DAY = 1000
    DELAY_BETWEEN_REQUESTS = 2.0  # segundos
    
    # Configurações de requisição
    TIMEOUT = 30