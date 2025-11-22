#!/usr/bin/env python3
"""
Script principal para salvar respostas COMPLETAS da API Mouser
"""

import time
from mouser_api_client import MouserApiClient

def main():
    """Função principal"""
    
    # Inicializa cliente da API
    client = MouserApiClient()
    
    print("🚀 Iniciando Mouser API Client")
    print("📡 Salvando respostas COMPLETAS da API (sem filtros)")
    print("💾 Todos os dados serão salvos em arquivos JSON")
    print("⏰ Delay entre requisições: 2 segundos")
    
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
    
    print(f"\n📋 Part numbers para processar: {len(part_numbers)}")
    print("📊 Serão gerados arquivos: COMPLETE_API_RESPONSE_<PART_NUMBER>.json")
    
    start_time = time.time()
    
    # Processa todos os part numbers
    successful = client.batch_save_responses(part_numbers)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resumo final
    print(f"\n{'='*80}")
    print("📊 RESUMO FINAL")
    print(f"{'='*80}")
    print(f"✅ Sucessos: {len(successful)}")
    print(f"❌ Falhas: {len(part_numbers) - len(successful)}")
    
    if part_numbers:
        success_rate = (len(successful) / len(part_numbers)) * 100
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    print(f"⏱️  Tempo total: {total_time:.2f} segundos")
    print(f"📁 Arquivos salvos: {len(successful)}")
    
    if successful:
        print("\n📄 Arquivos gerados:")
        for part_number in successful:
            print(f"   • COMPLETE_API_RESPONSE_{part_number}.json")
    
    print(f"\n🎯 Agora você pode analisar os arquivos JSON completos!")
    print("🔍 Examine os dados e identifique quais campos quer manter/filtrar.")

if __name__ == "__main__":
    main()