"""
Cliente para API Mouser - Salva resposta completa sem filtros
"""

import requests
import time
import logging
import json
from typing import List, Optional, Dict, Any

from config import MouserConfig

class MouserApiClient:
    """Cliente para API Mouser"""
    
    def __init__(self):
        self.config = MouserConfig()
        self.session = requests.Session()
        self.setup_logging()
        self.setup_session()
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mouser_api.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_session(self):
        """Configura a sessão HTTP"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def get_complete_api_response(self, part_number: str) -> Optional[Dict[str, Any]]:
        """
        Faz requisição para API e retorna TODOS os dados sem filtro
        
        Args:
            part_number (str): Número da peça a ser buscado
            
        Returns:
            dict: Resposta completa da API ou None em caso de erro
        """
        self.logger.info(f"🔍 Buscando part number: {part_number}")
        
        url = self.config.SEARCH_BY_PART_NUMBER_URL
        params = {'apiKey': self.config.API_KEY}
        
        payload = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number,
                "partSearchOptions": None
            }
        }
        
        try:
            response = self.session.post(
                url,
                params=params,
                json=payload,
                timeout=self.config.TIMEOUT
            )
            
            self.logger.info(f"📡 Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"✅ Resposta recebida para: {part_number}")
                
                # Log da estrutura básica para debug
                if 'SearchResults' in data:
                    num_results = data['SearchResults'].get('NumberOfResult', 0)
                    self.logger.info(f"📊 Número de resultados: {num_results}")
                
                return data
                
            else:
                self.logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"❌ Erro de requisição: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
            return None
        finally:
            # Respeita o rate limiting
            time.sleep(self.config.DELAY_BETWEEN_REQUESTS)
    
    def save_complete_response(self, part_number: str) -> bool:
        """
        Salva a resposta completa da API em arquivo JSON
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        complete_data = self.get_complete_api_response(part_number)
        
        if not complete_data:
            self.logger.error(f"❌ Não foi possível obter dados para: {part_number}")
            return False
        
        # Nome do arquivo
        filename = f"COMPLETE_API_RESPONSE_{part_number.replace('/', '_')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Resposta completa salva em: {filename}")
            
            # Log de informações básicas do arquivo salvo
            self._log_response_summary(complete_data, part_number)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar arquivo: {e}")
            return False
    
    def _log_response_summary(self, data: Dict[str, Any], part_number: str):
        """Loga um resumo da resposta para debug"""
        self.logger.info(f"📋 RESUMO DA RESPOSTA - {part_number}")
        
        if 'Errors' in data and data['Errors']:
            self.logger.warning(f"⚠️  Erros na resposta: {len(data['Errors'])}")
            for error in data['Errors']:
                self.logger.warning(f"   - {error.get('Message', 'Unknown error')}")
        
        if 'SearchResults' in data:
            search_results = data['SearchResults']
            num_results = search_results.get('NumberOfResult', 0)
            parts = search_results.get('Parts', [])
            
            self.logger.info(f"📊 Número de resultados: {num_results}")
            self.logger.info(f"🔧 Partes encontradas: {len(parts)}")
            
            if parts:
                first_part = parts[0]
                self.logger.info(f"🏭 Fabricante: {first_part.get('Manufacturer', 'N/A')}")
                self.logger.info(f"📝 Descrição: {first_part.get('Description', 'N/A')[:100]}...")
                self.logger.info(f"📎 Datasheet: {first_part.get('DataSheetUrl', 'N/A')}")
                
                # Informações sobre atributos
                attributes = first_part.get('ProductAttributes', [])
                self.logger.info(f"🔧 Atributos técnicos: {len(attributes)}")
                
                # Informações sobre preços
                price_breaks = first_part.get('PriceBreaks', [])
                self.logger.info(f"💰 Quebras de preço: {len(price_breaks)}")
    
    def batch_save_responses(self, part_numbers: List[str]) -> List[str]:
        """
        Processa uma lista de part numbers e salva as respostas completas
        
        Returns:
            List[str]: Lista de part numbers processados com sucesso
        """
        successful = []
        
        self.logger.info(f"📦 Processando lote de {len(part_numbers)} part numbers")
        
        for i, part_number in enumerate(part_numbers, 1):
            self.logger.info(f"🔧 [{i}/{len(part_numbers)}] Processando: {part_number}")
            
            try:
                success = self.save_complete_response(part_number)
                if success:
                    successful.append(part_number)
                else:
                    self.logger.warning(f"⚠️ Falha ao processar: {part_number}")
                    
            except KeyboardInterrupt:
                self.logger.info("⏹️  Processo interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar {part_number}: {e}")
                continue
        
        self.logger.info(f"✅ Lote processado: {len(successful)}/{len(part_numbers)} sucessos")
        return successful