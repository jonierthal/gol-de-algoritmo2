import os
import re
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play

# Carrega variáveis do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Diretórios
os.makedirs("audios", exist_ok=True)
os.makedirs("episodios", exist_ok=True)

# Vozes disponíveis na OpenAI
VOZES = {
    "RoboZé": "onyx",     # voz mais robótica/grave
    "DataLina": "nova"    # voz mais leve/feminina
}

# Remove instruções entre colchetes do texto
def limpar_texto(texto):
    return re.sub(r"\[.*?\]", "", texto).strip()

# Função para sintetizar texto usando OpenAI
def gerar_audio_openai(texto, nome_arquivo, voice):
    texto = limpar_texto(texto)
    
    response = client.audio.speech.create(
        model="tts-1",  # ou "tts-1-hd" para mais qualidade
        voice=voice,
        input=texto
    )

    with open(f"audios/{nome_arquivo}.mp3", "wb") as f:
        f.write(response.content)

# Divide o roteiro em falas por personagem
def separar_falas(roteiro):
    falas = []
    linhas = roteiro.splitlines()
    personagem_atual = None
    buffer = []

    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith("[") or linha.startswith("**["):
            continue

        match = re.match(r"(?:\*\*)?(.+?)(?:\*\*)?:\s*(.*)", linha)
        if match:
            if personagem_atual and buffer:
                falas.append((personagem_atual.strip(), limpar_texto(" ".join(buffer))))
                buffer = []

            personagem_atual = match.group(1).strip()
            conteudo = match.group(2).strip()
            if conteudo:
                buffer.append(conteudo)
        else:
            buffer.append(linha)

    if personagem_atual and buffer:
        falas.append((personagem_atual.strip(), limpar_texto(" ".join(buffer))))

    return falas

# Junta os áudios e monta o episódio final com vinheta
def montar_episodio(falas, nome_arquivo):
    trilha_final = AudioSegment.silent(duration=500)

    # Efeitos e trilhas
    intro_trilha = AudioSegment.from_mp3("efeitos/intro_trilha.mp3")
    outro_trilha = AudioSegment.from_mp3("efeitos/outro_trilha.mp3") - 22
    torcida = AudioSegment.from_mp3("efeitos/torcida.mp3") - 6
    apito = AudioSegment.from_mp3("efeitos/apito.mp3") - 3

    abertura = AudioSegment.from_mp3("audios/vinheta_abertura.mp3")
    vinheta_abertura = intro_trilha[:3000].fade_out(1000) + apito + torcida[:4000].fade_out(1000) + abertura
    trilha_final += vinheta_abertura + AudioSegment.silent(duration=500)

    falas_mix = AudioSegment.empty()
    for i, (personagem, _) in enumerate(falas):
        caminho = f"audios/fala_{i}_{personagem}.mp3"
        fala_audio = AudioSegment.from_mp3(caminho)
        fala_audio = fala_audio.fade_in(500).fade_out(500)
        falas_mix += fala_audio + AudioSegment.silent(duration=400)

    if len(outro_trilha) < len(falas_mix):
        outro_trilha *= int(len(falas_mix) / len(outro_trilha)) + 1

    trilha_com_fundo = falas_mix.overlay(outro_trilha[:len(falas_mix)] - 18)
    
    trilha_final += trilha_com_fundo

    encerramento = AudioSegment.from_mp3("audios/vinheta_encerramento.mp3")
    vinheta_encerramento = apito + torcida[:2000].fade_out(1000) + encerramento
    trilha_final += vinheta_encerramento

    output_path = f"episodios/{nome_arquivo}.mp3"
    trilha_final.export(output_path, format="mp3")
    print(f"\n✅ Episódio salvo em: {output_path}")

# Gera vinhetas com fala
def gerar_vinheta(nome, texto, voice):
    gerar_audio_openai(texto, nome, voice)

# Função principal do processo
def gerar_podcast_completo(roteiro):
    falas = separar_falas(roteiro)

    print("🧪 Falas detectadas:")
    for i, (p, f) in enumerate(falas):
        print(f"{i+1}. {p}: {f[:60]}...")

    print("🎤 Gerando áudios das falas...")
    for i, (personagem, texto) in enumerate(falas):
        voice = VOZES.get(personagem, "nova")  # fallback = DataLina
        nome_arquivo = f"fala_{i}_{personagem}"
        gerar_audio_openai(texto, nome_arquivo, voice)

    print("🎵 Gerando falas da vinheta de abertura e encerramento...")
    gerar_vinheta("vinheta_abertura", "Está no ar... Gol de Algoritmo! O podcast onde a bola rola com inteligência artificial!", "onyx")
    gerar_vinheta("vinheta_encerramento", "Esse foi mais um episódio do Gol de Algoritmo. Até a próxima rodada!", "nova")

    data_str = datetime.date.today().isoformat()
    montar_episodio(falas, nome_arquivo=data_str)
