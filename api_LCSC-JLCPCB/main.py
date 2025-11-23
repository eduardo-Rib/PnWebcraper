import requests
import json

def buscar_no_lcsc(part_number: str):
    """
    Consulta o part number usando a API pública do LCSC.
    """

    url = "https://wmsc.lcsc.com/wmsc/component/search"

    payload = {
        "currentPage": 1,
        "pageSize": 25,
        "keyword": part_number
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()

        data = r.json()

        comps = data.get("result", {}).get("components", [])
        if not comps:
            print("Nenhum resultado encontrado no LCSC.")
            return None

        comp = comps[0]

        resultado = {
            "lcsc_code": comp.get("productCode"),
            "nome": comp.get("title"),
            "marca": comp.get("brand"),
            "datasheet_url": comp.get("datasheetUrl"),
            "atributos": {att["name"]: att["value"] for att in comp.get("attributes", [])}
        }

        return resultado

    except Exception as e:
        print("Erro na requisição:", e)
        return None


if __name__ == "__main__":
    pn = "CL10C330JB8NNNC"
    dados = buscar_no_lcsc(pn)

    print(json.dumps(dados, indent=4, ensure_ascii=False))
