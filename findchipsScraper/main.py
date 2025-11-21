#!/usr/bin/env python3
"""
Script principal para scraping do Findchips
Processa um partnumber por vez conforme a fila do backend
"""

import json
import sys
import os

# Adiciona o diretório scraper ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from findchips_scraper import FindChipsScraper

def process_partnumber(partnumber):
    """
    Processa um único partnumber e retorna os resultados
    
    Args:
        partnumber (str): Número da peça a ser buscado
        
    Returns:
        dict: Resultados do scraping formatados para IA
    """
    print(f"🚀 Iniciando scraping para: {partnumber}")
    
    # Usando context manager para garantir que o driver seja fechado
    with FindChipsScraper(headless=True, timeout=30) as scraper:
        # Faz o scraping
        result = scraper.scrape_partnumber(partnumber)
        
        # Prepara dados para IA
        ai_ready_data = scraper.prepare_for_ai(result)
        
        return ai_ready_data

def main():
    """Função principal para teste"""
    partnumbers = [
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

    
    for partnumber in partnumbers:

        print(f"🔍 Buscando partnumber: {partnumber}")
        
        # Processa o partnumber
        result = process_partnumber(partnumber)
        
        # Exibe resultados
        print("\n" + "="*50)
        print("📊 RESULTADOS DO SCRAPING")
        print("="*50)
        
        print(f"Partnumber: {result['partnumber']}")
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")
        
        if result['status'] == 'success':
            print(f"Distribuidores encontrados: {result['distributors_count']}")
            print("\n📋 Distribuidores:")
            for i, distributor in enumerate(result['distributors'], 1):
                print(f"  {i}. {distributor['distributor_name']}")
                print(f"     URL: {distributor['product_url']}")
                if distributor.get('stock_info'):
                    print(f"     Estoque: {distributor['stock_info']}")
                if distributor.get('price_info'):
                    print(f"     Preço: {distributor['price_info']}")
                if distributor.get('html_content_preview'):
                    print(f"     HTML: {len(distributor['html_content_preview'])} caracteres")
                print()
        
        # Salva em JSON para inspeção
        output_file = f"result_{partnumber}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {output_file}")
        
    return result

if __name__ == "__main__":
    main()