# Configurações do Scraper
SCRAPER_CONFIG = {
    'headless': True,
    'timeout': 30,
    'delay_between_requests': 2,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Lista de distribuidores conhecidos
DISTRIBUTORS = {
    'digikey': 'Digi-Key',
    'mouser': 'Mouser', 
    'newark': 'Newark',
    'element14': 'Element14',
    'farnell': 'Farnell',
    'arrow': 'Arrow',
    'avnet': 'Avnet',
    'ttiinc': 'TTI',
    'futureelectronics': 'Future Electronics',
    'rs-online': 'RS Components'
}