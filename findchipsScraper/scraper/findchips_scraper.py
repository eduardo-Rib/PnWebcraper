import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urljoin, urlparse
import json

class FindChipsScraper:
    def __init__(self, headless=True, timeout=30):
        """
        Inicializa o scraper do Findchips
        
        Args:
            headless (bool): Executar em modo headless
            timeout (int): Timeout para espera de elementos
        """
        self.timeout = timeout
        self.headless = headless
        self.setup_logging()
        self.setup_selenium()
        
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_selenium(self):
        """Configura o Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("Selenium WebDriver inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Selenium: {e}")
            self.driver = None
    
    def scrape_partnumber(self, partnumber):
        """
        Faz scraping no Findchips para um partnumber específico
        
        Args:
            partnumber (str): Número da peça a ser buscado
            
        Returns:
            dict: Dados completos do scraping ou None se não encontrado
        """
        if not self.driver:
            self.logger.error("WebDriver não inicializado")
            return None
        
        url = f"https://www.findchips.com/search/{partnumber}"
        
        try:
            self.logger.info(f"Buscando partnumber: {partnumber}")
            self.driver.get(url)
            
            # Aguarda carregamento da página
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verifica se não encontrou resultados
            page_source = self.driver.page_source
            if "No results were found" in page_source:
                self.logger.warning(f"Partnumber {partnumber} não encontrado no Findchips")
                return {
                    'partnumber': partnumber,
                    'status': 'not_found',
                    'message': 'No results were found',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Extrai informações dos distribuidores
            distributors_data = self.extract_distributors_data()
            
            if not distributors_data:
                self.logger.warning(f"Nenhum distribuidor encontrado para {partnumber}")
                return {
                    'partnumber': partnumber,
                    'status': 'no_distributors',
                    'message': 'No distributors found',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            self.logger.info(f"Encontrados {len(distributors_data)} distribuidores para {partnumber}")
            
            # Para cada distribuidor, obtém o conteúdo HTML da página do produto
            for distributor in distributors_data:
                if distributor.get('product_url'):
                    html_content = self.get_distributor_page_content(
                        distributor['product_url']
                    )
                    distributor['page_html'] = html_content
                    # Pequeno delay entre requisições para evitar bloqueio
                    time.sleep(random.uniform(1, 3))
            
            return {
                'partnumber': partnumber,
                'status': 'success',
                'distributors_count': len(distributors_data),
                'distributors': distributors_data,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except TimeoutException:
            self.logger.error(f"Timeout ao acessar Findchips para {partnumber}")
            return {
                'partnumber': partnumber,
                'status': 'error',
                'message': 'Timeout accessing Findchips',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Erro ao fazer scraping no Findchips: {e}")
            return {
                'partnumber': partnumber,
                'status': 'error',
                'message': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def extract_distributors_data(self):
        """Extrai dados dos distribuidores da página do Findchips"""
        distributors_data = []
        
        try:
            # Tenta encontrar a tabela de distribuidores
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table, .table, .distributor-table, .results-table"))
            )
            
            # Encontra todas as linhas da tabela
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
            
            for row in rows:
                try:
                    distributor_info = self.extract_distributor_from_row(row)
                    if distributor_info and distributor_info.get('product_url'):
                        distributors_data.append(distributor_info)
                        
                except Exception as e:
                    self.logger.debug(f"Erro ao processar linha do distribuidor: {e}")
                    continue
                    
        except TimeoutException:
            self.logger.warning("Tabela de distribuidores não encontrada, tentando método alternativo")
            return self.extract_distributors_alternative()
        
        # Remove duplicatas baseado na URL
        return self.remove_duplicate_distributors(distributors_data)
    
    def extract_distributors_alternative(self):
        """Método alternativo para extrair dados de distribuidores"""
        distributors_data = []
        
        try:
            # Procura por links que possam ser de distribuidores
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and self.is_distributor_link(href):
                        distributor_data = {
                            'distributor_name': self.identify_distributor(href),
                            'product_url': href,
                            'link_text': link.text.strip()[:100]  # Limita o tamanho do texto
                        }
                        distributors_data.append(distributor_data)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro no método alternativo: {e}")
        
        return distributors_data
    
    def extract_distributor_from_row(self, row):
        """Extrai informações de um distribuidor de uma linha da tabela"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                return None
            
            # Procura por links na linha
            links = row.find_elements(By.TAG_NAME, "a")
            product_url = None
            distributor_name = None
            
            for link in links:
                href = link.get_attribute('href')
                if href and self.is_distributor_link(href):
                    product_url = href
                    distributor_name = self.identify_distributor(href)
                    break
            
            if not product_url:
                return None
            
            # Extrai outras informações
            stock_info = ""
            price_info = ""
            
            for cell in cells:
                text = cell.text.strip()
                if text:
                    if any(keyword in text.lower() for keyword in ['stock', 'qty', 'in stock', 'estoque']):
                        stock_info = text
                    elif any(keyword in text.lower() for keyword in ['price', '$', 'usd', 'preço']):
                        price_info = text
            
            return {
                'distributor_name': distributor_name,
                'product_url': product_url,
                'stock_info': stock_info,
                'price_info': price_info
            }
            
        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados do distribuidor: {e}")
            return None
    
    def remove_duplicate_distributors(self, distributors):
        """Remove distribuidores duplicados baseado na URL"""
        seen_urls = set()
        unique_distributors = []
        
        for distributor in distributors:
            url = distributor.get('product_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_distributors.append(distributor)
        
        return unique_distributors
    
    def is_distributor_link(self, url):
        """Verifica se o link é de um distribuidor conhecido"""
        distributor_domains = [
            'digikey', 'mouser', 'newark', 'element14', 'farnell',
            'arrow', 'avnet', 'ttiinc', 'futureelectronics', 'rs-online'
        ]
        return any(domain in url.lower() for domain in distributor_domains)
    
    def identify_distributor(self, url):
        """Identifica o nome do distribuidor baseado na URL"""
        url_lower = url.lower()
        distributors = {
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
        
        for domain, name in distributors.items():
            if domain in url_lower:
                return name
        
        return 'Distribuidor Desconhecido'
    
    def get_distributor_page_content(self, url):
        """
        Obtém o conteúdo HTML da página do distribuidor
        
        Args:
            url (str): URL da página do distribuidor
            
        Returns:
            str: HTML da página ou None em caso de erro
        """
        try:
            self.logger.info(f"Acessando página do distribuidor: {self.shorten_url(url)}")
            
            self.driver.get(url)
            
            # Aguarda o conteúdo principal carregar
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Aguarda um pouco mais para garantir que conteúdo dinâmico carregue
            time.sleep(2)
            
            return self.driver.page_source
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar página do distribuidor: {e}")
            return None
    
    def shorten_url(self, url, max_length=50):
        """Encurta URL para logging"""
        if len(url) <= max_length:
            return url
        return url[:max_length-3] + "..."
    
    def prepare_for_ai(self, scraping_result):
        """
        Prepara os dados do scraping para serem processados pela IA
        
        Args:
            scraping_result (dict): Resultado do scraping
            
        Returns:
            dict: Dados formatados para IA
        """
        if scraping_result['status'] != 'success':
            return scraping_result
        
        ai_data = scraping_result.copy()
        
        for distributor in ai_data['distributors']:
            # Remove o HTML completo para economizar espaço (pode ser readicionado se necessário)
            html_content = distributor.pop('page_html', None)
            if html_content:
                distributor['html_content_preview'] = html_content[:2000] + "..." if len(html_content) > 2000 else html_content
                distributor['html_content_length'] = len(html_content)
        
        return ai_data
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver fechado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()