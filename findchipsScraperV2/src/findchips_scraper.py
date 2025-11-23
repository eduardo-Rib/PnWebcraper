# src/findchips_scraper.py
import os
import json
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .config import FINDCHIPS_BASE, RESULTS_DIR
from .requester import Requester, AccessDeniedError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FindChipsScraper:
    def __init__(self, requester: Requester):
        self.requester = requester

    def build_search_url(self, partnumber: str) -> str:
        return f"{FINDCHIPS_BASE}/{partnumber}"

    def _parse_no_results(self, text: str, partnumber: str) -> bool:
        if f"No results were found for {partnumber}" in text:
            return True
        if f"no results were found for {partnumber}" in text.lower():
            return True
        # heurística: página sem resultados costuma ter expressões "no results" genéricas
        if "no results were found" in text.lower():
            return True
        return False

    def _extract_distributors(self, html: str) -> List[Dict[str,str]]:
        """
        heurística para extrair links de distribuidores:
        - busca por anchors externos (domínios != findchips.com)
        - tenta coletar texto do link como nome do distribuidor
        """
        soup = BeautifulSoup(html, "lxml")
        links = set()
        results = []

        # busca por containers óbvios
        containers = soup.find_all(class_=["results", "search-results", "search-result"])
        # se nenhum container, usa página inteira
        scope = containers if containers else [soup]

        for c in scope:
            for a in c.find_all("a", href=True):
                href = a["href"].strip()
                # ignore anchors internos
                if href.startswith("#") or href.startswith("/search") or "findchips.com" in href:
                    continue
                # se é um link relativo: ignore (é raro aqui), mas resolvemos depois
                text = (a.get_text(strip=True) or "").strip()
                links.add((href, text))

        # fallback: procurar qualquer anchor externo na página
        if not links:
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("http") and "findchips.com" not in href:
                    text = (a.get_text(strip=True) or "").strip()
                    links.add((href, text))

        # limpar e normalizar
        for href, text in links:
            # alguns hrefs são links findchips que redirecionam via clicktracking, tentar extrair destino
            if href.startswith("/"):
                # tornar absoluto usando base
                href = urljoin("https://www.findchips.com", href)
            parsed = urlparse(href)
            if not parsed.scheme:
                continue
            name = text if text else parsed.netloc
            results.append({"name": name, "url": href})

        # dedupe por url (preservando primeiro nome)
        seen = set()
        dedup = []
        for item in results:
            u = item["url"]
            if u in seen:
                continue
            seen.add(u)
            dedup.append(item)
        return dedup

    def search_partnumber(self, partnumber: str) -> List[Dict[str,str]]:
        url = self.build_search_url(partnumber)
        resp, reason = self.requester.get(url)
        if reason:
            # access denied ao consultar findchips (não queremos quebrar sua lógica; vamos reportar)
            logger.warning("Access denied ao acessar findchips: %s", reason)
            # nesse caso retornamos [] e informamos que houve bloqueio
            raise AccessDeniedError(f"Blocked when accessing findchips: {reason}")

        html = resp.text
        # Checar "no results"
        if self._parse_no_results(html, partnumber):
            logger.info("No results were found for %s on findchips", partnumber)
            return []

        distributors = self._extract_distributors(html)
        distributors = distributors[:10]

        return distributors
