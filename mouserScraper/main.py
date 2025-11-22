#!/usr/bin/env python3
"""
Script principal para uso do Mouser Scraper
"""

import json
import sys
import time
from mouser_scraper import MouserScraper

def process_part_number(part_number, scraper):
    """
    Processa um part number individual
    """
    print(f"\n{'='*80}")
    print(f"🔧 Processando: {part_number}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    # Faz o scraping
    product_data = scraper.scrape_product(part_number)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if product_data:
        print(f"✅ Sucesso! Tempo: {processing_time:.2f}s")
        
        # Exibe resumo dos dados
        print(f"📦 Título: {product_data.get('title', 'N/A')}")
        print(f"🏭 Fabricante: {product_data.get('manufacturer', 'N/A')}")
        print(f"🔢 Part Number: {product_data.get('part_number', 'N/A')}")
        print(f"📋 Descrição: {product_data.get('description', 'N/A')[:100]}...")
        print(f"📊 Especificações: {len(product_data.get('specifications', {}))} atributos")
        print(f"📎 Datasheet: {product_data.get('datasheet_url', 'N/A')}")
        print(f"📂 Categorias: {', '.join(product_data.get('categories', []))}")
        
        # Exibe algumas especificações importantes
        specs = product_data.get('specifications', {})
        if specs:
            print("\n📋 Principais especificações:")
            for i, (key, value) in enumerate(list(specs.items())[:10]):
                print(f"   {i+1:2d}. {key}: {value}")
            if len(specs) > 10:
                print(f"   ... e mais {len(specs) - 10} especificações")
        
        # Salva em JSON para inspeção
        filename = f"data_{part_number.replace('/', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Dados salvos em: {filename}")
        
        return product_data
    else:
        print(f"❌ Falha ao processar {part_number}")
        print(f"⏱️  Tempo: {processing_time:.2f}s")
        return None

def main():
    """Exemplo de uso"""
    
    # Inicializa o scraper com delay maior
    scraper = MouserScraper(delay=3.0)
    
    # Lista de part numbers para teste
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
    
    print("🚀 Iniciando Mouser Scraper (Versão Corrigida)")
    print(f"📋 Part numbers na fila: {len(part_numbers)}")
    print("⏰ Delay entre requisições: 3 segundos")
    
    results = []
    
    for i, part_number in enumerate(part_numbers, 1):
        print(f"\n📦 Item {i}/{len(part_numbers)}")
        try:
            result = process_part_number(part_number, scraper)
            if result:
                results.append(result)
        except KeyboardInterrupt:
            print("\n⏹️  Processo interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro inesperado com {part_number}: {e}")
            continue
    
    # Resumo final
    print(f"\n{'='*80}")
    print("📊 RESUMO FINAL")
    print(f"{'='*80}")
    print(f"✅ Sucessos: {len(results)}")
    print(f"❌ Falhas: {len(part_numbers) - len(results)}")
    if part_numbers:
        print(f"📈 Taxa de sucesso: {len(results)/len(part_numbers)*100:.1f}%")

if __name__ == "__main__":
    main()


