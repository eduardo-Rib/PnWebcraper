import time
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------

MOUSER_SEARCH_URL = "https://api.mouser.com/api/v1/search/partnumber"
API_KEY = "b6e26deb-732d-4771-9d90-02ea60ca3a21"  # coloque sua chave aqui

ua = UserAgent()

HEADERS = {
    "User-Agent": ua.random,
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
}


# ------------------------------------------------------------
# FUNÇÃO 1: Buscar o ProductDetailUrl pelo partnumber
# ------------------------------------------------------------

def get_product_detail_url(partnumber: str):
    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": partnumber,
            "partSearchOptions": "string"
        }
    }

    response = requests.post(
        f"{MOUSER_SEARCH_URL}?apiKey={API_KEY}",
        json=payload,
        headers=HEADERS
    )

    data = response.json()

    try:
        url = data["SearchResults"]["Parts"][0]["ProductDetailUrl"]
        return url
    except:
        return None


# ------------------------------------------------------------
# FUNÇÃO 2: Scraping do ProductDetailUrl
# ------------------------------------------------------------

def scrape_mouser_attributes(url: str):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    specs = {}

    # TABELA DE ATRIBUTOS TÉCNICOS
    table = soup.find("table", {"id": "product-specs"})

    if not table:
        return {"error": "Tabela de atributos não encontrada", "url": url}

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            attr_name = cols[0].get_text(strip=True)
            attr_value = cols[1].get_text(strip=True)
            specs[attr_name] = attr_value

    return specs


# ------------------------------------------------------------
# FUNÇÃO 3: Pipeline completo para um PN
# ------------------------------------------------------------

def process_partnumber(pn: str):
    print(f"\n🔍 Buscando URL do produto para: {pn}")
    url = get_product_detail_url(pn)

    if not url:
        print("❌ Não encontrei o ProductDetailUrl.")
        return {"partnumber": pn, "error": "URL não encontrada"}

    print(f"✔️ URL encontrada: {url}")
    print("⏳ Fazendo scraping...")

    attributes = scrape_mouser_attributes(url)

    return {
        "partnumber": pn,
        "url": url,
        "attributes": attributes
    }


# ------------------------------------------------------------
# FUNÇÃO 4: Fila de múltiplos partnumbers
# ------------------------------------------------------------

def process_queue(partnumbers: list, delay=4):
    results = []

    for pn in partnumbers:
        result = process_partnumber(pn)
        results.append(result)

        print(f"⏸️ Aguardando {delay} segundos antes do próximo...")
        time.sleep(delay)

    return results


# ------------------------------------------------------------
# EXECUÇÃO DE EXEMPLO
# ------------------------------------------------------------

if __name__ == "__main__":
    part_numbers = [
        "CL10C330JB8NNNC",
        "CL10B472KB8NNNC",
        "GRM1885C1H180JA01D",
        "CL10A106KP8NNNC",
        "C1608X5R1E106M080AC",
        "88512006119",
        "NACE100M100V6.3X8TR13F",
        "CRCW060320K0FKEA",
        "ERJ-2RKF2201X",
        "BC847BLT1G",
        "IRLML6401TRPBF",
        "STPS5H100B-TR",
        "ESD7C3.3DT5G",
        "LD1117ADT-TR REG",
        "ECS-3225Q-33-260-BS-TR"
    ]

    dados = process_queue(part_numbers)

    print("\n\n===== RESULTADO FINAL =====")
    print(json.dumps(dados, indent=4, ensure_ascii=False))
