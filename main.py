import os
import json
from datetime import datetime
from mutagen.mp3 import MP3  # Usando mutagen para MP3
import argparse
from noticias.coletar_noticias import coletar_noticias_ge
from gerar_roteiro import gerar_roteiro_gol_de_algoritmo
from Detalhes.gerar_detalhes import gerar_titulo, gerar_descricao
from gerar_audio import gerar_podcast_completo
from utils_feed import adicionar_item_feed

def calcular_duracao_arquivo_mp3(caminho_mp3):
    """
    Calcula a duração do arquivo MP3 e retorna no formato HH:MM:SS.
    """
    try:
        audio = MP3(caminho_mp3)
        segundos = int(audio.info.length)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60
        return f"{horas:02}:{minutos:02}:{segundos:02}"
    except Exception as e:
        print(f"⚠️ Erro ao calcular duração: {e}")
        return "00:00:00"

def main():
    parser = argparse.ArgumentParser(description="Gera episódio do Gol de Algoritmo")
    parser.add_argument("--com-audio", action="store_true", help="Gera o áudio do episódio (usa ElevenLabs)")
    args = parser.parse_args()

    print("🔍 Coletando notícias do dia...")
    noticias = coletar_noticias_ge()

    print("\n📰 Notícias encontradas:")
    for i, noticia in enumerate(noticias, 1):
        print(f"{i}. {noticia}")

    print("\n🧠 Gerando roteiro com base nas notícias...")
    roteiro = gerar_roteiro_gol_de_algoritmo(noticias)
    print("\n📜 Roteiro gerado:\n")
    print(roteiro)

    hoje = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("roteiro", exist_ok=True)

    caminho_roteiro = f"roteiro/roteiro_{hoje}.txt"
    with open(caminho_roteiro, "w", encoding="utf-8") as f:
        f.write(roteiro)
    print(f"\n📄 Roteiro salvo em: {caminho_roteiro}")

    titulo = gerar_titulo(roteiro.splitlines())
    descricao = gerar_descricao(roteiro.splitlines())

    print("\n🎙️ TÍTULO DO EPISÓDIO:")
    print(titulo)
    print("\n📝 DESCRIÇÃO DO EPISÓDIO:")
    print(descricao)

    dados_json = {
        "data": hoje,
        "titulo": titulo,
        "descricao": descricao,
        "roteiro": roteiro
    }

    # Geração de áudio
    if args.com_audio:
        print("\n🎧 Gerando áudio do episódio com ElevenLabs...")
        gerar_podcast_completo(roteiro)

        # Nome esperado do arquivo de áudio gerado
        nome_arquivo_mp3 = f"{hoje}.mp3"
        caminho_mp3 = os.path.join("episodios", nome_arquivo_mp3)


        # Verificando se o arquivo MP3 existe
        if os.path.exists(caminho_mp3):
            print(f"📂 Arquivo MP3 encontrado: {caminho_mp3}")

            # Captura a duração e o tamanho do MP3
            duracao = calcular_duracao_arquivo_mp3(caminho_mp3)
            tamanho = os.path.getsize(caminho_mp3)

            print(f"⏳ Duração: {duracao}")
            print(f"📏 Tamanho (bytes): {tamanho}")

            dados_json["arquivo"] = nome_arquivo_mp3
            dados_json["duracao"] = duracao
            dados_json["tamanho"] = tamanho

            # Atualiza feed.xml
            caminho_feed = "rss/feed.xml"
            caminho_json = f"roteiro/episodio_{hoje}.json"
            with open(caminho_json, "w", encoding="utf-8") as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)

            # Adiciona o item ao feed
            adicionar_item_feed(caminho_json, caminho_feed)
        else:
            print(f"⚠️ Arquivo MP3 não encontrado: {caminho_mp3}")
    else:
        print("\n🚫 Áudio não gerado (use --com-audio para ativar).")

        # Salva JSON mesmo sem áudio
        caminho_json = f"roteiro/episodio_{hoje}.json"
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=4)
        print(f"\n📁 Episódio parcial salvo (sem áudio) em: {caminho_json}")


if __name__ == "__main__":
    main()
