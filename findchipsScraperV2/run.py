# run.py
import sys
import logging
from src.master_scraper import MasterScraper
import json


logging.basicConfig(level=logging.INFO)

def main():
    partnumbers = [
        "CL10C330JB8NNNC"
        # "CL10B472KB8NNNC",
        # "GRM1885C1H180JA01D",
        # "CL10A106KP8NNNC",
        # "C1608X5R1E106M080AC",
        # "88512006119",
        # "NACE100M100V6.3X8TR13F",
        # "CRCW060320K0FKEA",
        # "ERJ-2RKF2201X",
        # "BC847BLT1G",
        # "IRLML6401TRPBF",
        # "STPS5H100B-TR",
        # "ESD7C3.3DT5G",
        # "LD1117ADT-TR REG",
        # "ECS-3225Q-33-260-BS-TR"
    ]
    

    for pn in partnumbers:
        master = MasterScraper()
        result = master.process_partnumber(pn)
        print("RESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    main()