# src/distributor_scraper.py
import os
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse
from .requester import Requester, AccessDeniedError
from .config import RESULTS_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DistributorScraper:
    def __init__(self, requester: Requester):
        self.requester = requester

    def fetch_and_save(self, partnumber: str, distributor: dict) -> Tuple[bool, Optional[str]]:
        """
        Tenta baixar a URL do distribuidor.
        Retorna (success, html_or_reason)
        - success=True: conteúdo HTML
        - success=False: motivo (ex: 'access_denied', 'request_error')
        """
        url = distributor.get("url")
        if not url:
            return False, "no_url"

        try:
            resp, reason = self.requester.get(url)
            if reason:
                logger.info("Access denied ao acessar %s: %s", url, reason)
                return False, f"access_denied:{reason}"

            # Em vez de salvar, retornamos o conteúdo HTML diretamente
            logger.info("Fetched HTML from %s", url)
            return True, resp.text  # Retorna o HTML diretamente

        except Exception as e:
            logger.exception("Error fetching %s: %s", url, e)
            return False, f"error:{e}"
