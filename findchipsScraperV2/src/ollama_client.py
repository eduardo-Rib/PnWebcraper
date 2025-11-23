import json
import yaml
import requests


class OllamaClient:
    def __init__(self, model_name: str = "qwen2.5:14b", 
                 prompt_path: str = "src/prompts/technical_extraction.yaml"):
        self.model_name = model_name
        self.prompt_path = prompt_path
        self.base_url = "http://localhost:11434/api/generate"

        # carregar template do prompt.yaml
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def build_prompt(self, partnumber: str, html: str) -> str:
        """
        Insere PN e HTML no template YAML.
        """
        return self.prompt_template.replace("{{partnumber}}", partnumber).replace("{{html}}", html)

    def extract_technical_data(self, partnumber: str, cleaned_html: str) -> dict:
        """
        Envia o prompt para o modelo Ollama e retorna o JSON.
        """
        prompt_text = self.build_prompt(partnumber, cleaned_html)

        payload = {
            "model": self.model_name,
            "prompt": prompt_text,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            raw = response.json()

            # O Ollama retorna geralmente em raw["response"]
            txt = raw.get("response", "").strip()

            # tentar decodificar como JSON
            try:
                parsed = json.loads(txt)
                return parsed
            except:
                return {
                    "partnumber": partnumber,
                    "status": "false",
                    "technical_data": {},
                    "message": "Model returned invalid JSON"
                }

        except Exception as e:
            return {
                "partnumber": partnumber,
                "status": "false",
                "technical_data": {},
                "message": f"Ollama error: {str(e)}"
            }
