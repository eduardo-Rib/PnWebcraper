"""
Configurações do Scraper Digi-Key
"""

# Configurações de Rate Limiting
REQUEST_DELAY = 5.0  # Delay base entre requisições
MAX_RETRIES = 3      # Máximo de tentativas por requisição
JITTER = True        # Adicionar variação aleatória nos delays

# Headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

# Timeouts
REQUEST_TIMEOUT = 20
CONNECTION_TIMEOUT = 10

# URLs
BASE_URL = "https://www.digikey.com"
SEARCH_URL = f"{BASE_URL}/en/products/result"