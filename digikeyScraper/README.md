# Digi-Key Scraper

Scraper para extração de dados técnicos de componentes eletrônicos do site Digi-Key.

## 🚀 Funcionalidades

- ✅ Busca por part number
- ✅ Extração de dados técnicos completos
- ✅ Download de link para datasheet
- ✅ Informações de preço
- ✅ Dados ambientais (RoHS, etc.)
- ✅ Rate limiting automático
- ✅ Tratamento de erros robusto

## 📦 Instalação

1. Clone o repositório
2. Crie ambiente virtual: `python -m venv venv`
3. Ative o ambiente:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale dependências: `pip install -r requirements.txt`

## ⚙️ Configuração
- delay: Delay entre requisições (padrão: 2.0s)

- Timeout: 15 segundos por requisição

- User-Agent: Chrome moderno para evitar bloqueios

## 📊 Estrutura dos Dados Retornados
```bash
{
  "success": true,
  "part_number": "LM358P",
  "url": "https://...",
  "product_name": "IC OPAMP GP 2 CIRCUIT 8DIP",
  "manufacturer": "Texas Instruments",
  "manufacturer_part_number": "LM358P",
  "digikey_part_number": "LM358P-ND",
  "datasheet_url": "https://...pdf",
  "product_description": "General Purpose Amplifier...",
  "technical_attributes": {
    "Operating Temperature": "-40°C ~ 85°C",
    "Voltage - Supply": "3V ~ 32V"
  },
  "pricing": [...],
  "environmental_data": {...},
  "product_images": [...]
}
```