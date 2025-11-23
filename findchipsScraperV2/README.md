# FindChips Scraper (Python)

Objetivo: buscar distribuidores em findchips.com para um partnumber e tentar baixar o HTML dos distribuidores, detectando access denied.

## Instalação
1. Crie / ative um venv:
   - `python -m venv venv`
   - Linux/macOS: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

2. Instale dependências:
   `pip install -r requirements.txt`

## Como rodar (exemplo)
`python run.py B32392A3224K189`

Isso executa o fluxo:
- consulta `https://www.findchips.com/search/<PN>`
- salva `distributors_<PN>.json` no diretório `./Results/`
- tenta baixar o HTML do primeiro distribuidor que não esteja bloqueado e salva em `./Results/`

## Integração com seu projeto
A classe `MasterScraper` em `src/master_scraper.py` é a interface única: chame `MasterScraper().process_partnumber(partnumber)` e receba:
- sucesso: dict com caminho do arquivo HTML salvo e metadados
- falha: dict indicando "technical data not found" ou que todos os distribuidores bloquearam.

Você pode adaptar `requester` para usar proxies ou headers customizados facilmente.
