# src/master_scraper.py
import os
import logging
from typing import Optional, Dict, Any, List

from .requester import Requester, AccessDeniedError
from .findchips_scraper import FindChipsScraper
from .distributor_scraper import DistributorScraper
from .html_cleaner import clean_html
from .ollama_client import OllamaClient   # <-- IMPORT FALTANTE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MasterScraper:
    def __init__(self, requester: Optional[Requester] = None):
        self.requester = requester or Requester()
        self.findchips = FindChipsScraper(self.requester)
        self.distributor_scraper = DistributorScraper(self.requester)

        # ADIÇÃO: registrar função de limpeza de HTML
        self.html_cleaner = clean_html

        # ADIÇÃO NECESSÁRIA: inicializar cliente Ollama
        self.ollama = OllamaClient(model_name="qwen2.5:14b")

    def process_partnumber(self, partnumber: str) -> Dict[str, Any]:

        try:
            distributors = self.findchips.search_partnumber(partnumber)
        except AccessDeniedError as e:
            return {
                "partnumber": partnumber,
                "status": "blocked_findchips",
                "saved_html": None,
                "message": str(e),
            }

        if not distributors:
            return {
                "partnumber": partnumber,
                "status": "not_found",
                "saved_html": None,
                "message": "technical data not found on findchips",
            }

        failed_reasons: List[str] = []

        # LOOP DE DISTRIBUIDORES
        failed_reasons: List[str] = []

        for dist in distributors:
            ok, htmlDistributor = self.distributor_scraper.fetch_and_save(partnumber, dist)

            if ok:
                # limpar HTML
                cleaned_html = self.html_cleaner(htmlDistributor)

                # enviar para IA do Ollama
                ai_result = self.ollama.extract_technical_data(partnumber, cleaned_html)

                # se a IA encontrar dados técnicos, fim!
                if ai_result.get("status") == "true":
                    return {
                        "partnumber": partnumber,
                        "status": "ok",
                        "technical_data": ai_result.get("technical_data", {}),
                        "message": ai_result.get("message", "Technical data found"),
                        "distributor_used": dist.get("name"),
                    }

                else:
                    # a IA não encontrou → tentar próximo distribuidor
                    failed_reasons.append(
                        f"AI failed for {dist.get('url')} ({ai_result.get('message')})"
                    )

            else:
                failed_reasons.append(f"{dist.get('url')} -> fetch failed")


        # nenhum distribuidor retornou dados técnicos
        return {
            "partnumber": partnumber,
            "status": "false",
            "technical_data": {},
            "message": "Technical data not found from any distributor",
            "details": failed_reasons,
        }