# src/html_cleaner.py
from bs4 import BeautifulSoup, Comment
import re

def clean_html(raw_html: str) -> str:
    """
    Limpeza genérica:
    - remove <script> e <style>
    - remove comentários
    - remove atributos inline que poluem (on* handlers, style)
    - remove tags vazias
    - minimiza longas sequências de whitespace
    - retorna HTML simplificado como string
    """
    soup = BeautifulSoup(raw_html, "lxml")

    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # remove comentários
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # remove atributos inline que não ajudam
    for tag in soup.find_all(True):
        # remover handlers JS e estilos inline e classes muito longas
        attrs = dict(tag.attrs)
        for a in attrs:
            if a.startswith("on"):  # onClick, onmouseover...
                del tag.attrs[a]
            elif a in ("style", "onclick", "onload"):
                if a in tag.attrs:
                    del tag.attrs[a]
        # opcional: manter id/class mínimos; não mexer em href/src
    # remover tags vazias (sem texto e sem filhos com texto)
    for tag in soup.find_all():
        if tag.name in ("meta", "link"):
            continue
        text = (tag.get_text(strip=True) or "")
        if not text and not tag.find(True):
            tag.decompose()

    # reduzir whitespace
    out = re.sub(r'\s{2,}', ' ', soup.prettify())

    return out.strip()
