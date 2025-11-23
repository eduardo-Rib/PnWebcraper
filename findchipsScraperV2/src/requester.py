# src/requester.py
import os
import time
import random
import logging
from typing import Optional, Tuple
import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


# ---- Fingerprints REALISTAS ---- #

FINGERPRINTS = [
    {
        "sec-ch-ua": '"Chromium";v="122", "Google Chrome";v="122", "Not A(Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "accept-language": "en-US,en;q=0.9",
    },
    {
        "sec-ch-ua": '"Google Chrome";v="121", "Chromium";v="121", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "upgrade-insecure-requests": "1",
        "accept-language": "en-US,en;q=0.8,pt-BR;q=0.7",
    },
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


class AccessDeniedError(Exception):
    pass


class Requester:
    """
    Requester ajustado especialmente para FindChips:
    - headers completos
    - fingerprint realista
    - cookies persistentes
    - warm-up para parecer browser humano
    - delays aleatórios
    """

    def __init__(
        self,
        timeout: int = 12,
        retries: int = 2,
        proxies: Optional[dict] = None,
        verify_tls: bool = True,
    ):
        self.timeout = timeout
        self.proxies = proxies
        self.verify_tls = verify_tls

        self.session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            backoff_factor=0.4,
            allowed_methods=["GET", "HEAD"],
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # WARM-UP: acessar página inicial sem PN para parecer uso humano
        self._warm_up()

    def _warm_up(self):
        """Acessa uma página neutra gerando cookies, fingerprint etc."""
        try:
            headers = self._generate_headers()
            self.session.get(
                "https://www.findchips.com/",
                headers=headers,
                timeout=self.timeout,
                proxies=self.proxies,
                verify=self.verify_tls,
            )
            time.sleep(random.uniform(0.8, 1.5))  # comportamento humano
        except:
            pass

    def _generate_headers(self, extra=None):
        fp = random.choice(FINGERPRINTS)
        ua = random.choice(USER_AGENTS)

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            **fp,
        }

        if extra:
            headers.update(extra)

        # aleatoriza a ordem de alguns headers para parecer navegador real
        headers_list = list(headers.items())
        random.shuffle(headers_list)
        headers = dict(headers_list)

        return headers

    def _check_access_denied(self, response: requests.Response):
        """Relaxado para FindChips — foco apenas em 403/429 reais"""
        if response.status_code in (403, 429):
            return f"status_{response.status_code}"

        # Não tratar 'captcha' como bloqueio automático — FindChips inclui isso em scripts
        text = response.text.lower()

        tokens = [
            "you have been blocked",
            "request blocked",
            "error 403",
        ]

        for token in tokens:
            if token in text:
                return token

        return None

    def get(self, url: str) -> Tuple[requests.Response, Optional[str]]:
        # atraso humano
        time.sleep(random.uniform(1.0, 2.5))

        try:
            headers = self._generate_headers()
            resp = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                proxies=self.proxies,
                verify=self.verify_tls,
            )

            reason = self._check_access_denied(resp)
            return resp, reason

        except Exception as e:
            logger.warning(f"[Requester Error] {url}: {e}")
            raise

    def save_response_html(self, response: requests.Response, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding=response.encoding or "utf-8") as f:
            f.write(response.text)
