# gerar_episodio.py

from openai import OpenAI
from config import OPENAI_API_KEY
import os
import json
from datetime import datetime

client = OpenAI(api_key=OPENAI_API_KEY)

FRASE_FINAL = (
    "Não fique de fora dessa conversa cheia de emoção e surpresas! "
    "Siga o 'Gol de Algoritmo' e fique por dentro do melhor que o futebol tem a oferecer!"
)

def gerar_roteiro(noticias: list) -> str:
    prompt = f"""
Você é roteirista de um podcast automatizado de futebol chamado "Gol de Algoritmo".
Seu objetivo é transformar as notícias abaixo em um roteiro descontraído, com tom humorado, mas com informações precisas.

Duas personas participam:
- RoboZé: torcedor raiz, emocionado, fanfarrão.
- DataLina: analítica, sarcástica e cheia de dados.

Notícias do dia:
{chr(10).join(f"- {n}" for n in noticias)}

Gere um roteiro com falas alternadas entre RoboZé e DataLina, com 2 a 3 minutos de duração (em texto). Comece com uma vinheta e termine com uma despedida.
"""

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um roteirista criativo especializado em podcasts esportivos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )

    return resposta.choices[0].message.content.strip()

def gerar_titulo(noticias: list) -> str:
    prompt = f"""
Você é um redator criativo especializado em títulos para podcasts.

Crie um título criativo e chamativo (com até 100 caracteres) para um episódio do podcast 'Gol de Algoritmo', que fala sobre futebol com um toque de humor e inteligência artificial.

As principais notícias abordadas são:
{chr(10).join(f"- {n}" for n in noticias)}

O título pode conter emojis, trocadilhos ou referências culturais, mas deve ser claro sobre os temas.
"""

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em marketing de podcasts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=100
    )

    return resposta.choices[0].message.content.strip().strip('"')

def gerar_descricao(noticias: list) -> str:
    prompt = f"""
Você é um roteirista de podcast esportivo.
Crie uma descrição envolvente para o episódio do podcast 'Gol de Algoritmo'.
O episódio comenta com humor e informação as seguintes notícias:
{chr(10).join(f"- {n}" for n in noticias)}

A descrição deve conter até 1000 caracteres, ser fluida, natural, com tom descontraído, e terminar com esta frase:
{FRASE_FINAL}
"""

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente criativo para descrição de podcasts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=600
    )

    return resposta.choices[0].message.content.strip().strip('"')

def salvar_episodio(dados: dict, caminho: str = "roteiro/episodio.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def gerar_episodio_completo(noticias: list):
    titulo = gerar_titulo(noticias)
    descricao = gerar_descricao(noticias)
    roteiro = gerar_roteiro(noticias)
    
    dados = {
        "data": datetime.now().strftime("%Y-%m-%d"),
        "titulo": titulo,
        "descricao": descricao,
        "roteiro": roteiro,
        "noticias": noticias
    }

    salvar_episodio(dados)
    print("✅ Episódio gerado com sucesso e salvo em JSON!")

# Exemplo de uso
if __name__ == "__main__":
    noticias_exemplo = [
        "Flamengo vence o clássico contra o Vasco por 3 a 1",
        "Palmeiras anuncia novo reforço vindo da Europa",
        "Seleção Brasileira feminina se prepara para a Copa do Mundo"
    ]
    gerar_episodio_completo(noticias_exemplo)
