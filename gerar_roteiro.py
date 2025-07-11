# gerar_roteiro.py

import os
from config import OPENAI_API_KEY
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Cria o cliente da nova API OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def gerar_roteiro_gol_de_algoritmo(noticias: list, salvar_em: str = "roteiro/roteiro.txt") -> str:
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

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um roteirista criativo especializado em podcasts esportivos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )

    roteiro = response.choices[0].message.content

    os.makedirs(os.path.dirname(salvar_em), exist_ok=True)

    with open(salvar_em, "w", encoding="utf-8") as f:
        f.write(roteiro)

    return roteiro
