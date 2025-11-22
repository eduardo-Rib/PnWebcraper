#!/usr/bin/env python3
"""
Teste rápido para um único part number
"""

import json
import time
from mouser_scraper import MouserScraper

def test_single_part_number(part_number):
    """Testa um único part number"""
    print(f"🧪 Testando part number: {part_number}")
    
    scraper = MouserScraper(delay=5.0)  # Delay maior para evitar bloqueio
    
    start_time = time.time()
    product_data = scraper.scrape_product(part_number)
    end_time = time.time()
    
    if product_data and not product_data.get('error'):
        print(f"✅ SUCESSO! Tempo: {end_time - start_time:.2f}s")
        print(f"📦 Título: {product_data.get('title')}")
        print(f"🏭 Fabricante: {product_data.get('manufacturer')}")
        print(f"🔢 Part Number: {product_data.get('part_number')}")
        print(f"📊 Especificações: {len(product_data.get('specifications', {}))}")
        print(f"📎 Datasheet: {product_data.get('datasheet_url')}")
        
        # Salva os dados
        filename = f"TEST_{part_number}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Salvo em: {filename}")
        
        return True
    else:
        error_msg = product_data.get('error') if product_data else "Falha no scraping"
        print(f"❌ FALHA: {error_msg}")
        print(f"⏱️ Tempo: {end_time - start_time:.2f}s")
        return False

if __name__ == "__main__":
    # Teste com o part number que você mencionou
    part_number = "CL10C330JB8NNNC"
    success = test_single_part_number(part_number)
    
    if not success:
        print("\n🔧 Tentando solução alternativa...")
        # Tentativa com approach diferente
        print("Se ainda não funcionar, podemos tentar:")
        print("1. Usar Selenium com WebDriver")
        print("2. Utilizar API oficial da Mouser")
        print("3. Usar serviço de scraping profissional")