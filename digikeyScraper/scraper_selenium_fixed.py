import time
import random
import logging
import sys
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import re

class DigiKeySeleniumScraper:
    def __init__(self, headless: bool = True, delay: float = 5.0):
        """
        Inicializa o scraper com Selenium WebDriver - Versão Corrigida
        
        Args:
            headless: Executar em modo headless (sem interface gráfica)
            delay: Delay base entre ações
        """
        self.delay = delay
        self.headless = headless
        self.driver = None
        self.wait = None
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self._setup_driver()

    def _setup_driver(self):
        """Configura o WebDriver do Chrome com fallbacks robustos"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Opções avançadas para evitar detecção
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")
        
        # Estratégias de fallback para o WebDriver
        driver_paths = [
            # 1. Tentar usar webdriver-manager primeiro
            self._try_webdriver_manager,
            # 2. Tentar ChromeDriver no PATH
            self._try_chromedriver_path,
            # 3. Tentar usar Chrome diretamente (se estiver no PATH padrão)
            self._try_chrome_default
        ]
        
        for driver_method in driver_paths:
            try:
                self.logger.info(f"Tentando método: {driver_method.__name__}")
                driver_method(chrome_options)
                if self.driver:
                    self.logger.info("✅ WebDriver inicializado com sucesso")
                    return
            except Exception as e:
                self.logger.warning(f"❌ Método {driver_method.__name__} falhou: {e}")
                continue
        
        raise WebDriverException("Todos os métodos de inicialização do WebDriver falharam")

    def _try_webdriver_manager(self, chrome_options):
        """Tenta usar webdriver-manager para baixar e gerenciar o ChromeDriver"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType
            
            # Forçar versão compatível
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self._post_driver_setup()
            
        except Exception as e:
            raise WebDriverException(f"WebDriver Manager falhou: {e}")

    def _try_chromedriver_path(self, chrome_options):
        """Tenta usar ChromeDriver do PATH do sistema"""
        try:
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self._post_driver_setup()
            
        except Exception as e:
            raise WebDriverException(f"ChromeDriver do PATH falhou: {e}")

    def _try_chrome_default(self, chrome_options):
        """Tenta usar Chrome instalado no local padrão"""
        try:
            # Locais padrão do Chrome no Windows
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]
            
            for path in chrome_paths:
                try:
                    chrome_options.binary_location = path
                    service = Service()
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self._post_driver_setup()
                    return
                except:
                    continue
                    
            raise WebDriverException("Chrome não encontrado nos locais padrão")
            
        except Exception as e:
            raise WebDriverException(f"Chrome padrão falhou: {e}")

    def _post_driver_setup(self):
        """Configurações pós-inicialização do driver"""
        if self.driver:
            # Esconder automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            self.wait = WebDriverWait(self.driver, 20)
            
            # Configurar timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)

    def _human_delay(self, min_multiplier=0.5, max_multiplier=2.0):
        """Aguarda um tempo aleatório simulando comportamento humano"""
        delay = self.delay * random.uniform(min_multiplier, max_multiplier)
        time.sleep(delay)

    def scrape_product_data(self, part_number: str) -> Dict:
        """
        Método principal: busca e extrai dados técnicos por part number
        """
        try:
            self.logger.info(f"🚀 Iniciando busca para: {part_number}")
            
            # Passo 1: Buscar a página do produto
            product_url = self._find_product_url(part_number)
            if not product_url:
                return {
                    'success': False,
                    'error': f'Produto não encontrado: {part_number}',
                    'part_number': part_number
                }
            
            self.logger.info(f"✅ URL encontrada: {product_url}")
            
            # Passo 2: Extrair dados da página
            product_data = self._extract_product_page_data(product_url)
            
            if product_data:
                product_data.update({
                    'success': True,
                    'part_number': part_number,
                    'url': product_url
                })
                self.logger.info(f"📊 Dados extraídos com sucesso: {part_number}")
                return product_data
            else:
                return {
                    'success': False,
                    'error': f'Falha ao extrair dados da página: {part_number}',
                    'part_number': part_number,
                    'url': product_url
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado para {part_number}: {str(e)}")
            return {
                'success': False,
                'error': f'Erro inesperado: {str(e)}',
                'part_number': part_number
            }

    def _find_product_url(self, part_number: str) -> Optional[str]:
        """
        Encontra a URL do produto usando Selenium
        """
        try:
            # Vá para a página inicial primeiro
            self.driver.get("https://www.digikey.com")
            self._human_delay(3, 5)
            
            # Aguarde a página carregar
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Tente diferentes seletores para a barra de pesquisa
            search_selectors = [
                "input#header-search-input",
                "input[placeholder*='Search']",
                "input[type='search']",
                "input.search-input"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if not search_box:
                self.logger.error("Não foi possível encontrar a barra de pesquisa")
                return None
            
            # Limpe e digite o part number
            search_box.clear()
            self._human_delay(1, 2)
            
            # Digitação lenta simulando humano
            for char in part_number:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            self._human_delay(1, 2)
            
            # Encontre e clique no botão de pesquisa
            search_buttons = [
                "button[type='submit']",
                "button.search-button",
                "input[type='submit']"
            ]
            
            search_button = None
            for selector in search_buttons:
                try:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if search_button:
                search_button.click()
            else:
                # Se não encontrar botão, tente Enter
                search_box.send_keys("\n")
            
            # Aguarde os resultados carregarem
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self._human_delay(3, 5)
            
            # Verifique se estamos em uma página de produto ou resultados
            current_url = self.driver.current_url
            if "/en/products/detail/" in current_url:
                return current_url
            
            # Se estamos nos resultados, encontre o primeiro produto
            product_selectors = [
                "a[data-testid='product-detail-link']",
                "a[href*='/en/products/detail/']",
                ".product-link",
                "tr td:first-child a"
            ]
            
            for selector in product_selectors:
                try:
                    product_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_links:
                        product_url = product_links[0].get_attribute("href")
                        if product_url and "/en/products/detail/" in product_url:
                            return product_url
                except:
                    continue
            
            return None
            
        except TimeoutException:
            self.logger.error(f"Timeout ao buscar produto: {part_number}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao buscar URL para {part_number}: {e}")
            return None

    def _extract_product_page_data(self, url: str) -> Optional[Dict]:
        """
        Extrai dados técnicos da página do produto
        """
        try:
            # Navegue para a URL se necessário
            if self.driver.current_url != url:
                self.driver.get(url)
                self._human_delay(3, 5)
            
            # Aguarde a página carregar completamente
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self._human_delay(2, 3)
            
            # Role a página para carregar todo o conteúdo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_delay(1, 2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            self._human_delay(1, 2)
            
            # Obtenha o HTML da página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            product_data = {
                'product_name': self._extract_product_name(soup),
                'manufacturer': self._extract_manufacturer(soup),
                'manufacturer_part_number': self._extract_manufacturer_part_number(soup),
                'digikey_part_number': self._extract_digikey_part_number(soup),
                'datasheet_url': self._extract_datasheet(soup),
                'product_description': self._extract_product_description(soup),
                'technical_attributes': self._extract_technical_attributes(soup),
                'pricing': self._extract_pricing(soup),
                'environmental_data': self._extract_environmental_data(soup),
                'product_images': self._extract_images(soup)
            }
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da página {url}: {e}")
            return None

    # ... (métodos de extração mantidos da versão anterior)
    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extrai o nome do produto"""
        try:
            selectors = [
                'h1[data-testid="product-name"]',
                'h1.product-name',
                'h1',
                '.product-details h1',
                '#product-name'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)
                    
        except Exception as e:
            self.logger.warning(f"Erro ao extrair nome do produto: {e}")
            
        return ""

    def _extract_manufacturer(self, soup: BeautifulSoup) -> str:
        """Extrai o nome do fabricante"""
        try:
            selectors = [
                'a[href*="/en/products/detail/"]',
                '[data-testid="manufacturer-name"]',
                '.manufacturer-name',
                'td:contains("Manufacturer") + td',
                'th:contains("Manufacturer") + td'
            ]
            
            for selector in selectors:
                if 'contains' in selector:
                    element = soup.find(lambda tag: tag.name and 'manufacturer' in tag.get_text().lower())
                    if element:
                        return element.get_text(strip=True)
                else:
                    element = soup.select_one(selector)
                    if element and element.get_text(strip=True):
                        return element.get_text(strip=True)
                        
        except Exception as e:
            self.logger.warning(f"Erro ao extrair fabricante: {e}")
            
        return ""

    def _extract_manufacturer_part_number(self, soup: BeautifulSoup) -> str:
        """Extrai o part number do fabricante"""
        try:
            patterns = [
                r'Manufacturer Part Number',
                r'Mfr\. Part Number',
                r'Part Number',
                r'MPN'
            ]
            
            for pattern in patterns:
                element = soup.find(string=re.compile(pattern, re.IGNORECASE))
                if element:
                    parent = element.find_parent()
                    if parent:
                        value_element = parent.find_next(string=True)
                        if value_element:
                            return value_element.strip()
                            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair part number do fabricante: {e}")
            
        return ""

    def _extract_digikey_part_number(self, soup: BeautifulSoup) -> str:
        """Extrai o part number da Digi-Key"""
        try:
            patterns = [
                r'DigiKey Part Number',
                r'Digi-Key Part Number',
                r'Customer Part Number'
            ]
            
            for pattern in patterns:
                element = soup.find(string=re.compile(pattern, re.IGNORECASE))
                if element:
                    parent = element.find_parent()
                    if parent:
                        value_element = parent.find_next(string=True)
                        if value_element:
                            return value_element.strip()
                            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair part number da Digi-Key: {e}")
            
        return ""

    def _extract_datasheet(self, soup: BeautifulSoup) -> str:
        """Extrai URL do datasheet"""
        try:
            datasheet_links = soup.find_all('a', href=re.compile(r'datasheet|\.pdf', re.IGNORECASE))
            
            for link in datasheet_links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if 'datasheet' in text or href.endswith('.pdf'):
                    if href.startswith('http'):
                        return href
                    else:
                        return "https://www.digikey.com" + href
                        
        except Exception as e:
            self.logger.warning(f"Erro ao extrair datasheet: {e}")
            
        return ""

    def _extract_product_description(self, soup: BeautifulSoup) -> str:
        """Extrai descrição do produto"""
        try:
            selectors = [
                '[data-testid="product-description"]',
                '.product-description',
                '.description',
                '.overview',
                '#productDescription'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)
                    
        except Exception as e:
            self.logger.warning(f"Erro ao extrair descrição: {e}")
            
        return ""

    def _extract_technical_attributes(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai a tabela de atributos técnicos"""
        attributes = {}
        
        try:
            # Procura por tabelas de especificações
            spec_tables = soup.find_all('table', class_=re.compile(r'spec|attribute', re.IGNORECASE))
            
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    
                    if th and td:
                        key = th.get_text(strip=True)
                        value = td.get_text(strip=True)
                        
                        if key and value and key not in attributes:
                            attributes[key] = value
            
            # Procura também por divs com atributos
            attr_sections = soup.find_all('div', class_=re.compile(r'attribute|spec', re.IGNORECASE))
            
            for section in attr_sections:
                label = section.find(class_=re.compile(r'label|name', re.IGNORECASE))
                value = section.find(class_=re.compile(r'value|data', re.IGNORECASE))
                
                if label and value:
                    key = label.get_text(strip=True)
                    val = value.get_text(strip=True)
                    if key and val and key not in attributes:
                        attributes[key] = val
                        
        except Exception as e:
            self.logger.warning(f"Erro ao extrair atributos técnicos: {e}")
            
        return attributes

    def _extract_pricing(self, soup: BeautifulSoup) -> list:
        """Extrai tabela de preços"""
        pricing = []
        
        try:
            price_tables = soup.find_all('table', class_=re.compile(r'price', re.IGNORECASE))
            
            for table in price_tables:
                rows = table.find_all('tr')[1:]  # Pula cabeçalho
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        quantity = cells[0].get_text(strip=True)
                        price = cells[1].get_text(strip=True)
                        
                        if quantity and price:
                            pricing.append({
                                'quantity': quantity,
                                'price': price
                            })
                            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair preços: {e}")
            
        return pricing

    def _extract_environmental_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai dados ambientais"""
        environmental = {}
        
        try:
            env_keywords = ['rohs', 'environmental', 'export', 'compliance', 'msl']
            
            for keyword in env_keywords:
                elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
                for element in elements:
                    parent = element.find_parent()
                    if parent:
                        key = element.get_text(strip=True)
                        value_element = parent.find_next(string=True)
                        if value_element:
                            environmental[key] = value_element.strip()
                            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados ambientais: {e}")
            
        return environmental

    def _extract_images(self, soup: BeautifulSoup) -> list:
        """Extrai URLs das imagens do produto"""
        images = []
        
        try:
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src', '')
                if src and any(keyword in src.lower() for keyword in ['product', 'image', 'photo']):
                    if src.startswith('http'):
                        images.append(src)
                    elif src.startswith('//'):
                        images.append('https:' + src)
                    else:
                        images.append("https://www.digikey.com" + src)
                        
        except Exception as e:
            self.logger.warning(f"Erro ao extrair imagens: {e}")
            
        return images

    def close(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver fechado")
            except:
                pass