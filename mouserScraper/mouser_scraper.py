import requests
import time
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, quote, unquote
import logging
from typing import Dict, Optional, List
import random

class MouserScraper:
    def __init__(self, delay: float = 2.0, timeout: int = 15):
        self.session = requests.Session()
        self.delay = delay
        self.timeout = timeout
        self.setup_headers()
        self.setup_logging()
        
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mouser_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_headers(self):
        """Configura headers para simular um navegador real"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.session.headers.update(self.headers)
    
    def add_random_delay(self):
        """Adiciona um delay aleatório entre requisições"""
        delay = self.delay * (0.8 + random.random() * 0.4)  # Entre 0.8x e 1.2x do delay
        self.logger.info(f"⏳ Aguardando {delay:.2f} segundos...")
        time.sleep(delay)
    
    def clean_part_number(self, part_number: str) -> str:
        """Limpa e formata o part number para URL"""
        return quote(part_number.strip().upper())
    
    def build_search_url(self, part_number: str) -> str:
        """Constrói URL de busca para o part number"""
        clean_pn = self.clean_part_number(part_number)
        return f"https://www.mouser.com/c/?q={clean_pn}"
    
    def extract_product_links(self, soup: BeautifulSoup, part_number: str) -> List[str]:
        """Extrai links de produtos da página de busca"""
        product_links = []
        
        self.logger.info("🔍 Procurando links de produtos...")
        
        # Estratégia 1: Procurar por elementos de produto na página de resultados
        product_selectors = [
            'a[href*="/ProductDetail/"]',
            '.product-link[href*="/ProductDetail/"]',
            '.mfr-part-num a[href*="/ProductDetail/"]',
            '.search-results a[href*="/ProductDetail/"]',
            'tr a[href*="/ProductDetail/"]',
            '.ProductTable a[href*="/ProductDetail/"]'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            self.logger.info(f"🔍 Seletor '{selector}' encontrou {len(links)} links")
            
            for link in links:
                href = link.get('href')
                if href and '/ProductDetail/' in href:
                    full_url = urljoin('https://www.mouser.com', href)
                    
                    # Verifica se o part number está na URL ou no texto do link
                    link_text = link.get_text(strip=True).upper()
                    if (part_number.upper() in full_url.upper() or 
                        part_number.upper() in link_text or
                        self.is_similar_part_number(part_number, link_text)):
                        
                        if full_url not in product_links:
                            product_links.append(full_url)
                            self.logger.info(f"✅ Link válido encontrado: {full_url}")
            
            if product_links:
                break
        
        # Estratégia 2: Se não encontrou links, tentar encontrar por texto
        if not product_links:
            self.logger.info("🔍 Tentando busca por texto...")
            all_links = soup.find_all('a', href=True, string=True)
            for link in all_links:
                href = link.get('href')
                link_text = link.get_text(strip=True).upper()
                
                if ('/ProductDetail/' in href and 
                    (part_number.upper() in link_text or 
                     self.is_similar_part_number(part_number, link_text))):
                    
                    full_url = urljoin('https://www.mouser.com', href)
                    if full_url not in product_links:
                        product_links.append(full_url)
                        self.logger.info(f"✅ Link encontrado por texto: {full_url}")
        
        # Estratégia 3: Tentar construir URL manualmente se nenhum link foi encontrado
        if not product_links:
            self.logger.info("🔍 Tentando construir URL manualmente...")
            # Remove espaços e caracteres especiais para a URL
            clean_pn_url = part_number.replace(' ', '%20').replace('/', '%2F')
            manual_url = f"https://www.mouser.com/ProductDetail/{clean_pn_url}"
            product_links.append(manual_url)
            self.logger.info(f"🔧 URL manual construída: {manual_url}")
        
        return product_links
    
    def is_similar_part_number(self, original: str, candidate: str) -> bool:
        """Verifica se dois part numbers são similares"""
        original_clean = original.upper().replace(' ', '').replace('-', '')
        candidate_clean = candidate.upper().replace(' ', '').replace('-', '')
        
        # Considera similar se pelo menos 80% dos caracteres coincidem
        if len(original_clean) > 0:
            common_chars = sum(1 for a, b in zip(original_clean, candidate_clean) if a == b)
            similarity = common_chars / len(original_clean)
            return similarity >= 0.8
        
        return False
    
    def extract_product_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extrai dados técnicos do produto da página de detalhes"""
        product_data = {
            'url': url,
            'title': '',
            'manufacturer': '',
            'part_number': '',
            'description': '',
            'datasheet_url': '',
            'specifications': {},
            'image_url': '',
            'technical_attributes': {},
            'categories': [],
            'price_breaks': [],
            'availability': '',
            'rohs_status': '',
            'error': None
        }
        
        try:
            self.logger.info("📖 Extraindo dados do produto...")
            
            # 1. Extrair título do produto
            title_selectors = [
                'h1',
                '.product-title',
                '.product-details h1',
                'h1[data-testid="product-name"]',
                '.product-name h1',
                '.product-header h1',
                '#productTitle',
                '.title',
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text(strip=True)
                    if product_data['title']:
                        self.logger.info(f"📝 Título encontrado: {product_data['title']}")
                        break
            
            # 2. Extrair fabricante
            manufacturer_selectors = [
                '[data-testid="manufacturer-name"]',
                '.mfr-part-number span',
                '.manufacturer-name',
                '.mfr-name',
                '.brand',
                '.vendor',
                'td:contains("Manufacturer") + td',
                'th:contains("Manufacturer") + td',
            ]
            
            for selector in manufacturer_selectors:
                mfr_elem = soup.select_one(selector)
                if mfr_elem:
                    product_data['manufacturer'] = mfr_elem.get_text(strip=True)
                    if product_data['manufacturer']:
                        self.logger.info(f"🏭 Fabricante encontrado: {product_data['manufacturer']}")
                        break
            
            # 3. Extrair part number
            part_number_selectors = [
                '[data-testid="mfr-part-number"]',
                '.mfr-part-number',
                '.part-number',
                '.mfr-part-num',
                '.sku',
                'td:contains("Mfr Part #") + td',
                'td:contains("Part Number") + td',
                'th:contains("Mfr Part #") + td',
            ]
            
            for selector in part_number_selectors:
                pn_elem = soup.select_one(selector)
                if pn_elem:
                    text = pn_elem.get_text(strip=True)
                    # Remove labels comuns
                    for label in ['Mfr Part #:', 'Part Number:', 'Mfr Part #', 'Part Number']:
                        if label in text:
                            text = text.split(label, 1)[1].strip()
                    product_data['part_number'] = text
                    if product_data['part_number']:
                        self.logger.info(f"🔢 Part Number encontrado: {product_data['part_number']}")
                        break
            
            # 4. Extrair descrição
            description_selectors = [
                '[data-testid="product-description"]',
                '.product-description',
                '.description-text',
                '.prod-desc',
                '.product-details .description',
                'meta[name="description"]',
            ]
            
            for selector in description_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    if selector == 'meta[name="description"]':
                        product_data['description'] = desc_elem.get('content', '').strip()
                    else:
                        product_data['description'] = desc_elem.get_text(strip=True)
                    
                    if product_data['description']:
                        self.logger.info(f"📋 Descrição encontrada ({len(product_data['description'])} chars)")
                        break
            
            # 5. Extrair datasheet
            datasheet_selectors = [
                'a[href*="datasheet"]',
                'a[href*="Datasheet"]',
                'a[href*=".pdf"]',
                '.data-sheet',
                '.datasheet-link',
                '[data-testid="datasheet-link"]',
                'a:contains("Datasheet")',
            ]
            
            for selector in datasheet_selectors:
                ds_elem = soup.select_one(selector)
                if ds_elem and ds_elem.get('href'):
                    href = ds_elem.get('href')
                    if '.pdf' in href.lower():
                        product_data['datasheet_url'] = urljoin('https://www.mouser.com', href)
                        self.logger.info(f"📎 Datasheet encontrado: {product_data['datasheet_url']}")
                        break
            
            # 6. Extrair imagem do produto
            image_selectors = [
                '.product-image img',
                '.main-product-image img',
                '[data-testid="product-image"]',
                '.gallery img',
                '.product-img img',
                'img[alt*="product"]',
                'img[src*="product"]',
            ]
            
            for selector in image_selectors:
                img_elem = soup.select_one(selector)
                if img_elem and img_elem.get('src'):
                    src = img_elem.get('src')
                    if not src.startswith('data:'):  # Ignora imagens em base64
                        product_data['image_url'] = urljoin('https://www.mouser.com', src)
                        self.logger.info(f"🖼️ Imagem encontrada")
                        break
            
            # 7. Extrair especificações técnicas
            self._extract_specifications(soup, product_data)
            
            # 8. Extrair atributos técnicos adicionais
            self._extract_technical_attributes(soup, product_data)
            
            # 9. Extrair categorias
            self._extract_categories(soup, product_data)
            
            # 10. Extrair informações de preço e disponibilidade
            self._extract_pricing_availability(soup, product_data)
            
            self.logger.info(f"✅ Dados extraídos: {len(product_data['specifications'])} especificações")
            
        except Exception as e:
            error_msg = f"Erro ao extrair dados do produto: {str(e)}"
            self.logger.error(error_msg)
            product_data['error'] = error_msg
        
        return product_data
    
    def _extract_specifications(self, soup: BeautifulSoup, product_data: Dict):
        """Extrai tabela de especificações técnicas"""
        try:
            # Procura por diferentes estruturas de tabela de especificações
            spec_selectors = [
                'table',
                '.specs-table',
                '.specifications table',
                '.technical-specifications table',
                '[data-testid="specifications"] table',
                '.product-specifications table',
                '.attr-table',
                '.parameters table',
            ]
            
            all_tables = soup.find_all('table')
            self.logger.info(f"📊 Encontradas {len(all_tables)} tabelas na página")
            
            for table in all_tables:
                self._parse_spec_table(table, product_data)
            
            # Se não encontrou na estrutura de tabela, tenta outras estruturas
            if not product_data['specifications']:
                self._extract_specifications_alternative(soup, product_data)
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair especificações: {e}")
    
    def _parse_spec_table(self, table, product_data: Dict):
        """Parseia uma tabela de especificações"""
        try:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Pega o primeiro e segundo cell
                    attribute = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if (attribute and value and 
                        len(attribute) < 100 and  # Evita textos muito longos
                        attribute not in ['Attribute', 'Specification', 'Característica', ''] and
                        not attribute.startswith('#')):
                        
                        # Limpa o atributo
                        attribute = re.sub(r'[:：]$', '', attribute).strip()
                        product_data['specifications'][attribute] = value
                        
        except Exception as e:
            self.logger.debug(f"Erro ao parsear tabela: {e}")
    
    def _extract_specifications_alternative(self, soup: BeautifulSoup, product_data: Dict):
        """Tenta extrair especificações de estruturas alternativas"""
        try:
            # Procura por divs com pares atributo/valor
            spec_divs = soup.select('.spec-item, .spec-row, .attribute-item, .param-row, .tech-spec')
            self.logger.info(f"🔍 Procurando especificações alternativas: {len(spec_divs)} divs encontradas")
            
            for div in spec_divs:
                attribute_elem = div.select_one('.spec-name, .attribute-name, .spec-label, .param-name, .name, .label')
                value_elem = div.select_one('.spec-value, .attribute-value, .spec-data, .param-value, .value, .data')
                
                if attribute_elem and value_elem:
                    attribute = attribute_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    if attribute and value:
                        product_data['specifications'][attribute] = value
            
            # Procura por listas de definição
            dl_elements = soup.select('dl')
            for dl in dl_elements:
                dt_elements = dl.select('dt')
                dd_elements = dl.select('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    attribute = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if attribute and value:
                        product_data['specifications'][attribute] = value
                        
        except Exception as e:
            self.logger.error(f"Erro ao extrair especificações alternativas: {e}")
    
    def _extract_technical_attributes(self, soup: BeautifulSoup, product_data: Dict):
        """Extrai atributos técnicos adicionais"""
        try:
            # Usa as especificações como base para atributos técnicos
            product_data['technical_attributes'] = product_data['specifications'].copy()
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair atributos técnicos: {e}")
    
    def _extract_categories(self, soup: BeautifulSoup, product_data: Dict):
        """Extrai categorias do produto"""
        try:
            category_selectors = [
                '.breadcrumb a',
                '.breadcrumbs a',
                '.category-path a',
                '[data-testid="breadcrumb"] a',
                '.nav-path a',
            ]
            
            for selector in category_selectors:
                categories = soup.select(selector)
                for category in categories:
                    cat_text = category.get_text(strip=True)
                    if (cat_text and 
                        cat_text.lower() not in ['home', 'mouser', 'products', 'product'] and
                        len(cat_text) > 2 and  # Filtra textos muito curtos
                        cat_text not in product_data['categories']):
                        product_data['categories'].append(cat_text)
                
                if product_data['categories']:
                    self.logger.info(f"📂 Categorias encontradas: {len(product_data['categories'])}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Erro ao extrair categorias: {e}")
    
    def _extract_pricing_availability(self, soup: BeautifulSoup, product_data: Dict):
        """Extra informações de preço e disponibilidade"""
        try:
            # Disponibilidade
            availability_selectors = [
                '.availability',
                '.stock',
                '[data-testid="stock"]',
                '.inventory',
                '.qty-available',
                'td:contains("Stock") + td',
                'th:contains("Stock") + td',
            ]
            
            for selector in availability_selectors:
                elem = soup.select_one(selector)
                if elem:
                    product_data['availability'] = elem.get_text(strip=True)
                    if product_data['availability']:
                        break
            
            # Status RoHS
            rohs_selectors = [
                '[data-testid="rohs"]',
                '.rohs',
                '.rohs-status',
                '.compliance-rohs',
                'td:contains("RoHS") + td',
                'th:contains("RoHS") + td',
            ]
            
            for selector in rohs_selectors:
                elem = soup.select_one(selector)
                if elem:
                    product_data['rohs_status'] = elem.get_text(strip=True)
                    if product_data['rohs_status']:
                        break
            
            if product_data['availability']:
                self.logger.info(f"📦 Disponibilidade: {product_data['availability']}")
            if product_data['rohs_status']:
                self.logger.info(f"🌱 RoHS: {product_data['rohs_status']}")
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair preço/disponibilidade: {e}")
    
    def scrape_product(self, part_number: str) -> Optional[Dict]:
        """
        Função principal que faz o scraping para um part number
        
        Args:
            part_number (str): Número da peça a ser buscado
            
        Returns:
            dict: Dados do produto ou None se não encontrado
        """
        self.logger.info(f"🚀 Iniciando scraping para: {part_number}")
        
        try:
            # 1. Fazer busca
            search_url = self.build_search_url(part_number)
            self.logger.info(f"🔍 Buscando em: {search_url}")
            
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 2. Verificar se estamos em uma página de produto
            current_url = response.url
            if '/ProductDetail/' in current_url:
                product_url = current_url
                self.logger.info(f"🎯 Já na página do produto: {product_url}")
            else:
                # 3. Extrair links de produtos
                product_links = self.extract_product_links(soup, part_number)
                
                if not product_links:
                    self.logger.warning(f"❌ Nenhum produto encontrado para: {part_number}")
                    return None
                
                product_url = product_links[0]
                self.logger.info(f"✅ Produto selecionado: {product_url}")
            
            # 4. Acessar página do produto
            self.logger.info(f"📄 Acessando página do produto...")
            product_response = self.session.get(product_url, timeout=self.timeout)
            product_response.raise_for_status()
            
            # Verificar se não foi redirecionado para página de busca
            if '/Search/Refine' in product_response.url:
                self.logger.warning(f"❌ Redirecionado para página de busca: {part_number}")
                return None
            
            product_soup = BeautifulSoup(product_response.content, 'html.parser')
            
            # 5. Extrair dados do produto
            product_data = self.extract_product_data(product_soup, product_response.url)
            
            # 6. Verificar se encontrou dados suficientes
            if not product_data['title'] and not product_data['specifications']:
                self.logger.warning(f"⚠️ Dados insuficientes encontrados para: {part_number}")
                return None
            
            self.logger.info(f"✅ Scraping concluído com sucesso para: {part_number}")
            return product_data
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Erro na requisição para {part_number}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado para {part_number}: {e}")
            return None
        finally:
            # Delay para evitar bloqueio
            self.add_random_delay()