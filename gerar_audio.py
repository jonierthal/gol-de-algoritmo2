# gerar_audio.py

import os
import re
import datetime
import requests
from pydub import AudioSegment
from config import ELEVENLABS_API_KEY
from pydub.playback import play

# Diretórios
os.makedirs("audios", exist_ok=True)
os.makedirs("episodios", exist_ok=True)

# IDs reais das vozes
VOZES = {
    "RoboZé": "IKne3meq5aSn9XLyUdCD",     # Charlie
    "DataLina": "EXAVITQu4vr4xnSDxMaL"     # Sarah
}

# Remove instruções entre colchetes do texto
def limpar_texto(texto):
    return re.sub(r"\[.*?\]", "", texto).strip()

# Função para sintetizar texto usando ElevenLabs
def gerar_audio(texto, nome_arquivo, voice):
    texto = limpar_texto(texto)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        with open(f"audios/{nome_arquivo}.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Erro ao gerar áudio: {response.status_code} - {response.text}")

# Divide o roteiro em falas por personagem
def separar_falas(roteiro):
    falas = []
    linhas = roteiro.splitlines()
    personagem_atual = None
    buffer = []

    for linha in linhas:
        linha = linha.strip()

        # Ignora linhas com efeitos sonoros ou instruções
        if not linha or linha.startswith("[") or linha.startswith("**["):
            continue

        # Detecta nova fala com ou sem asteriscos
        match = re.match(r"(?:\*\*)?(.+?)(?:\*\*)?:\s*(.*)", linha)
        if match:
            # Salva a fala anterior
            if personagem_atual and buffer:
                falas.append((personagem_atual.strip(), limpar_texto(" ".join(buffer))))
                buffer = []

            personagem_atual = match.group(1).strip()
            conteudo = match.group(2).strip()
            if conteudo:
                buffer.append(conteudo)
        else:
            buffer.append(linha)

    # Salva a última fala
    if personagem_atual and buffer:
        falas.append((personagem_atual.strip(), limpar_texto(" ".join(buffer))))

    return falas


# Junta os áudios e monta o episódio final com vinheta

def montar_episodio(falas, nome_arquivo):
    trilha_final = AudioSegment.silent(duration=500)

    # Efeitos e trilhas
    intro_trilha = AudioSegment.from_mp3("efeitos/intro_trilha.mp3")
    outro_trilha = AudioSegment.from_mp3("efeitos/outro_trilha.mp3") - 22  # reduz volume da música de fundo
    torcida = AudioSegment.from_mp3("efeitos/torcida.mp3") - 6
    apito = AudioSegment.from_mp3("efeitos/apito.mp3") - 3

    # Vinheta de abertura (fala + efeitos)
    abertura = AudioSegment.from_mp3("audios/vinheta_abertura.mp3")
    vinheta_abertura = intro_trilha[:3000].fade_out(1000) + apito + torcida[:4000].fade_out(1000) + abertura
    trilha_final += vinheta_abertura + AudioSegment.silent(duration=500)

    # Concatenar falas com música de fundo contínua
    falas_mix = AudioSegment.empty()
    for i, (personagem, _) in enumerate(falas):
        caminho = f"audios/fala_{i}_{personagem}.mp3"
        fala_audio = AudioSegment.from_mp3(caminho)

        # Aplica transição suave
        fala_audio = fala_audio.fade_in(500).fade_out(500)
        
        falas_mix += fala_audio + AudioSegment.silent(duration=400)

    # Loop da música de fundo conforme necessário
    if len(outro_trilha) < len(falas_mix):
        n_repeticoes = int(len(falas_mix) / len(outro_trilha)) + 1
        outro_trilha = outro_trilha * n_repeticoes

    trilha_com_fundo = falas_mix.overlay(outro_trilha[:len(falas_mix)])
    trilha_final += trilha_com_fundo

    # Vinheta de encerramento (fala + efeitos)
    encerramento = AudioSegment.from_mp3("audios/vinheta_encerramento.mp3")
    vinheta_encerramento = apito + torcida[:2000].fade_out(1000) + encerramento
    trilha_final += vinheta_encerramento

    # Exportar episódio
    output_path = f"episodios/{nome_arquivo}.mp3"
    trilha_final.export(output_path, format="mp3")
    print(f"\n✅ Episódio salvo em: {output_path}")

# Gera vinhetas com fala
def gerar_vinheta(nome, texto, voice):
    gerar_audio(texto, nome, voice)

# Função principal do processo
def gerar_podcast_completo(roteiro):
    falas = separar_falas(roteiro)

    print("🧪 Falas detectadas:")
    for i, (p, f) in enumerate(falas):
        print(f"{i+1}. {p}: {f[:60]}...")

    print("🎤 Gerando áudios das falas...")
    for i, (personagem, texto) in enumerate(falas):
        voice = VOZES.get(personagem, "EXAVITQu4vr4xnSDxMaL")  # fallback = DataLina
        nome_arquivo = f"fala_{i}_{personagem}"
        gerar_audio(texto, nome_arquivo, voice)

    print("🎵 Gerando falas da vinheta de abertura e encerramento...")
    gerar_vinheta("vinheta_abertura", "Está no ar... Gol de Algoritmo! O podcast onde a bola rola com inteligência artificial!", "IKne3meq5aSn9XLyUdCD")
    gerar_vinheta("vinheta_encerramento", "Esse foi mais um episódio do Gol de Algoritmo. Até a próxima rodada!", "EXAVITQu4vr4xnSDxMaL")

    data_str = datetime.date.today().isoformat()
    montar_episodio(falas, nome_arquivo=data_str)
