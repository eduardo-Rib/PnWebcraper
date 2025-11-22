"""
Configurações do Mouser Scraper
"""

# Configurações de scraping
SCRAPER_CONFIG = {
    'delay_between_requests': 1.0,  # segundos
    'request_timeout': 15,
    'max_retries': 2,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
}

# Campos esperados no resultado
EXPECTED_FIELDS = [
    'title',
    'manufacturer', 
    'part_number',
    'description',
    'datasheet_url',
    'specifications',
    'technical_attributes',
    'categories',
    'availability'
]