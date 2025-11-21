import json
import time
import random
from old_selenium.scraper_selenium import DigiKeySeleniumScraper
import logging

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper_selenium.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """Função principal para testar o scraper com Selenium"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Lista reduzida para teste
    test_part_numbers = [
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
    
    successful = 0
    failed = 0
    scraper = None
    
    try:
        # Inicializa o scraper (modo headless = True para não abrir janela)
        scraper = DigiKeySeleniumScraper(headless=True, delay=3.0)
        
        for i, part_number in enumerate(test_part_numbers):
            logger.info(f"🔍 Processando {i+1}/{len(test_part_numbers)}: {part_number}")
            
            result = scraper.scrape_product_data(part_number)
            
            if result['success']:
                successful += 1
                print(f"\n✅ SUCESSO: {part_number}")
                print(f"📝 Nome: {result.get('product_name', 'N/A')}")
                print(f"🏭 Fabricante: {result.get('manufacturer', 'N/A')}")
                print(f"🔗 Datasheet: {result.get('datasheet_url', 'N/A')}")
                print(f"📊 Atributos técnicos encontrados: {len(result.get('technical_attributes', {}))}")
                
                # Exibe alguns atributos importantes
                tech_attrs = result.get('technical_attributes', {})
                for attr, value in list(tech_attrs.items())[:5]:  # Mostra apenas os 5 primeiros
                    print(f"   • {attr}: {value}")
                
                # Salva em JSON para análise
                with open(f'result_selenium_{part_number}.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                    
            else:
                failed += 1
                print(f"\n❌ FALHA: {part_number}")
                print(f"   Erro: {result.get('error', 'Erro desconhecido')}")
            
            print("-" * 80)
            
            # Delay maior entre part numbers
            if i < len(test_part_numbers) - 1:
                extra_delay = random.uniform(10, 20)
                logger.info(f"⏳ Aguardando {extra_delay:.1f}s antes do próximo...")
                time.sleep(extra_delay)
        
        # Estatísticas finais
        print(f"\n📈 RESULTADO FINAL:")
        print(f"   ✅ Sucessos: {successful}")
        print(f"   ❌ Falhas: {failed}")
        print(f"   📊 Taxa de sucesso: {(successful/len(test_part_numbers))*100:.1f}%")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
    finally:
        if scraper:
            scraper.close()
        logger.info("Scraper finalizado")

if __name__ == "__main__":
    main()