# Findchips Scraper

Scraper para extrair dados técnicos de componentes eletrônicos do site Findchips.com.

---

## Funcionalidades

- Busca partnumbers no Findchips
- Extrai links para distribuidores (Digi-Key, Mouser, Newark, etc.)
- Obtém HTML completo das páginas dos distribuidores
- Formata dados para processamento por IA
- Processa um partnumber por vez (ideal para filas)

---

## Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd findchips_scraper
pip install -r requirements.txt
python main.py
```

---

## Estrutura de Saída

{
  "partnumber": "B32392A3224K189",
  "status": "success",
  "distributors_count": 3,
  "distributors": [
    {
      "distributor_name": "Digi-Key",
      "product_url": "https://www.digikey.com/...",
      "stock_info": "In stock: 1500",
      "price_info": "$1.50",
      "html_content_preview": "...",
      "html_content_length": 15420
    }
  ],
  "timestamp": "2024-01-15 10:30:45"
}

---

Status pssíveis

- success: Partnumber encontrado com distribuidores

- not_found: Partnumber não encontrado no Findchips

- no_distributors: Partnumber encontrado mas sem links de distribuidores

- error: Erro durante o scraping