import argparse
import os
import json
from datetime import datetime

from noticias.coletar_noticias import coletar_noticias_ge
from gerar_roteiro import gerar_roteiro_gol_de_algoritmo
from Detalhes.gerar_detalhes import gerar_titulo, gerar_descricao
from gerar_audio import gerar_podcast_completo


def main():
    # Argumentos de terminal
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

    # Diretório para salvar os arquivos
    hoje = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("roteiro", exist_ok=True)

    # Salva o roteiro em .txt
    caminho_roteiro = f"roteiro/roteiro_{hoje}.txt"
    with open(caminho_roteiro, "w", encoding="utf-8") as f:
        f.write(roteiro)
    print(f"\n📄 Roteiro salvo em: {caminho_roteiro}")

    # Gera título e descrição para Spotify
    titulo = gerar_titulo(roteiro.splitlines())
    descricao = gerar_descricao(roteiro.splitlines())

    print("\n🎙️ TÍTULO DO EPISÓDIO:")
    print(titulo)

    print("\n📝 DESCRIÇÃO DO EPISÓDIO:")
    print(descricao)

    # Salva episódio completo em .json
    dados_json = {
        "data": hoje,
        "titulo": titulo,
        "descricao": descricao,
        "roteiro": roteiro
    }

    caminho_json = f"roteiro/episodio_{hoje}.json"
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=4)
    print(f"\n📁 Episódio completo salvo em: {caminho_json}")

    # Geração de áudio (opcional)
    if args.com_audio:
        print("\n🎧 Gerando áudio do episódio com ElevenLabs...")
        gerar_podcast_completo(roteiro)
    else:
        print("\n🚫 Áudio não gerado (use --com-audio para ativar).")


if __name__ == "__main__":
    main()
