# Web Scraper para Componentes Eletrônicos
Este projeto contém sistemas de web scraping para extrair dados técnicos de componentes eletrônicos a partir de part numbers.

---

## 🎯 Objetivo
Integrar com um sistema existente que:

- Extrai part numbers de PDFs

- Busca dados técnicos dos produtos

- Processa informações com agentes de IA para descrição e classificação

---

## 🔧 Versões Disponíveis
1. Scraper FindChips
- Busca informações técnicas no site FindChips

- Foco em dados de distribuidores e disponibilidade

- Estrutura otimizada para extração multi-fornecedor

- Entra na pagina do prodito e extrai o HTML

- Manda esse HTML para uma IA encontrar os dados tecnicos (Qwen)

## 2. Scraper Digi-Key
- Busca informações técnicas no site Digi-Key

- Extração detalhada de atributos técnicos, datasheets e especificações

- Múltiplas estratégias anti-bloqueio (Selenium + requests)

---

## 📊 Status
Ambas as versões estão em desenvolvimento ativo, testando eficácia contra proteções anti-bot e qualidade da extração de dados técnicos.

- **FindChips** Precisa de uma IA para funcionar, entao demanda mais tempo de processamento

- **Digi-Key** Não demanda uma IA para funcionar, mas tem muitos bloqueios de Scraping