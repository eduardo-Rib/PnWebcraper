import os
import time
import json
import requests
from fake_useragent import UserAgent

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------

MOUSER_SEARCH_URL = "https://api.mouser.com/api/v1/search/partnumber"
API_KEY = "" 

ua = UserAgent()

HEADERS = {
    "User-Agent": ua.random,
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
}

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


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
# FUNÇÃO 2: Baixar o HTML bruto da página do produto
# ------------------------------------------------------------

def download_html(url: str):
    response = requests.get(url, headers=HEADERS)

    print(response)

    if response.status_code != 200:
        return None
    
    return response.text


# ------------------------------------------------------------
# FUNÇÃO 3: Pipeline completo para 1 PN
# ------------------------------------------------------------

def process_partnumber(pn: str):
    print(f"\nBuscando URL do produto para: {pn}")
    url = get_product_detail_url(pn)

    if not url:
        print("Não encontrei o ProductDetailUrl.")
        return {"partnumber": pn, "error": "URL não encontrada"}

    print(f"URL encontrada: {url}")
    print("Baixando HTML bruto...")

    html = download_html(url)

    if not html:
        print("Erro ao baixar HTML")
        return {"partnumber": pn, "url": url, "error": "Falha ao baixar HTML"}

    # Salvar HTML em arquivo
    filename = os.path.join(TEMP_DIR, f"{pn}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML salvo em: {filename}")

    return {
        "partnumber": pn,
        "url": url,
        "html_file": filename,
        "html_length": len(html)
    }


# ------------------------------------------------------------
# FUNÇÃO 4: Fila de múltiplos PNs
# ------------------------------------------------------------

def process_queue(partnumbers: list, delay=4):
    results = []

    for pn in partnumbers:
        result = process_partnumber(pn)
        results.append(result)

        print(f"Aguardando {delay} segundos antes do próximo...")
        time.sleep(delay)

    return results


# ------------------------------------------------------------
# EXECUÇÃO DE EXEMPLO
# ------------------------------------------------------------

if __name__ == "__main__":
    fila = [
        "CL10C330JB8NNNC"
    ]

    dados = process_queue(fila)

    print("\n\n===== RESULTADO FINAL =====")
    print(json.dumps(dados, indent=4, ensure_ascii=False))




# part_numbers = [
#         "CL10C330JB8NNNC", ok
#         "CL10B472KB8NNNC", ok
#         "GRM1885C1H180JA01D", ok
#         "CL10A106KP8NNNC", ok
#         "C1608X5R1E106M080AC",
#         "88512006119", ok
#         "NACE100M100V6.3X8TR13F", not ok
#         "CRCW060320K0FKEA", ok
#         "ERJ-2RKF2201X", ok
#         "BC847BLT1G", ok
#         "IRLML6401TRPBF", ok
#         "STPS5H100B-TR", ok
#         "ESD7C3.3DT5G", ok
#         "LD1117ADT-TR REG", ok
#         "ECS-3225Q-33-260-BS-TR" ok
#     ]
