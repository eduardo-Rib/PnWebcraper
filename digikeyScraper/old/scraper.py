import requests
from bs4 import BeautifulSoup
import time
import re
import random
from typing import Dict, Optional
import logging
from urllib.parse import quote

class DigiKeyScraper:
    def __init__(self, delay: float = 5.0, max_retries: int = 3):
        """
        Inicializa o scraper com proteções anti-bloqueio
        
        Args:
            delay: Delay entre requisições (aumentado para 5s)
            max_retries: Número máximo de tentativas
        """
        self.session = requests.Session()
        self.delay = delay
        self.max_retries = max_retries
        
        # Headers mais realistas e variados
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        self._update_headers()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _update_headers(self):
        """Atualiza headers com User-Agent aleatório"""
        self.headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,pt;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def _request_with_retry(self, url: str, params: dict = None) -> requests.Response:
        """
        Faz requisição com retry automático e delays aleatórios
        """
        for attempt in range(self.max_retries):
            try:
                # Atualiza headers a cada tentativa
                self._update_headers()
                
                # Delay exponencial + aleatório
                if attempt > 0:
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    self.logger.info(f"Tentativa {attempt + 1}/{self.max_retries}. Aguardando {wait_time:.2f}s")
                    time.sleep(wait_time)
                
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=20,
                    allow_redirects=True
                )
                
                if response.status_code == 429:
                    self.logger.warning(f"Erro 429 - Too Many Requests. Tentativa {attempt + 1}")
                    continue
                elif response.status_code == 403:
                    self.logger.warning(f"Erro 403 - Forbidden. Tentativa {attempt + 1}")
                    continue
                elif response.status_code == 200:
                    return response
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Erro na tentativa {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
        
        raise requests.exceptions.RequestException(f"Falha após {self.max_retries} tentativas")

    def scrape_product_data(self, part_number: str) -> Dict:
        """
        Método principal: busca e extrai dados técnicos por part number
        """
        try:
            self.logger.info(f"🚀 Iniciando busca para: {part_number}")
            
            # Delay inicial antes de começar
            time.sleep(self.delay + random.uniform(1, 2))
            
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
        Encontra a URL do produto usando estratégias múltiplas
        """
        try:
            # Estratégia 1: Busca direta na API de busca
            search_url = "https://www.digikey.com/en/products/result"
            params = {
                "keywords": part_number,
                "mpart": part_number,
            }
            
            response = self._request_with_retry(search_url, params)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estratégia 1A: Busca por links de produtos
            product_links = soup.find_all('a', href=re.compile(r'/en/products/detail/'))
            
            for link in product_links[:3]:  # Limita a 3 primeiros resultados
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                # Verifica se o part number está no link ou no texto
                if (part_number.lower() in href.lower() or 
                    part_number.lower() in link_text.lower()):
                    full_url = "https://www.digikey.com" + href
                    return full_url
            
            # Estratégia 1B: Pega o primeiro resultado se não encontrou match exato
            if product_links:
                first_link = product_links[0].get('href')
                return "https://www.digikey.com" + first_link
            
            # Estratégia 2: Tenta construção direta da URL
            direct_url = self._build_direct_url(part_number)
            if direct_url:
                return direct_url
                
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar URL para {part_number}: {e}")
            return None

    def _build_direct_url(self, part_number: str) -> Optional[str]:
        """
        Tenta construir a URL diretamente (fallback)
        """
        try:
            # Padrão comum: /en/products/detail/fabricante/partnumber/id
            # Como não sabemos o fabricante, tentamos um padrão genérico
            test_url = f"https://www.digikey.com/en/products/detail/{part_number}"
            response = self.session.head(test_url, headers=self.headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return test_url
        except:
            pass
        
        return None

    def _extract_product_page_data(self, url: str) -> Optional[Dict]:
        """
        Extrai dados técnicos da página do produto
        """
        try:
            # Delay antes de acessar a página do produto
            time.sleep(self.delay + random.uniform(0.5, 1.5))
            
            response = self._request_with_retry(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
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

    # ... (os métodos de extração _extract_product_name, _extract_manufacturer, etc. permanecem os mesmos)
    # Mantenha todos os métodos de extração da versão anterior

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
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    
                    if th and td:
                        key = th.get_text(strip=True)
                        value = td.get_text(strip=True)
                        
                        if key and value and key not in attributes:
                            attributes[key] = value
            
            attr_containers = soup.find_all('div', class_=re.compile(r'attribute|spec', re.IGNORECASE))
            
            for container in attr_containers:
                label = container.find(class_=re.compile(r'label|name', re.IGNORECASE))
                value = container.find(class_=re.compile(r'value|data', re.IGNORECASE))
                
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
                rows = table.find_all('tr')[1:]
                
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
        """Fecha a sessão"""
        self.session.close()