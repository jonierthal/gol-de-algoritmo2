import xml.etree.ElementTree as ET
from datetime import datetime
import os

def adicionar_item_feed(caminho_json, caminho_feed):
    import json

    # Lê os dados do episódio do JSON
    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    titulo = dados['titulo']
    descricao = dados['descricao']
    arquivo_mp3 = dados['arquivo']
    duracao = dados['duracao']
    tamanho = str(dados['tamanho'])

    # Data para pubDate (ex: "Mon, 14 Jul 2025 11:00:00 GMT")
    data_obj = datetime.strptime(dados['data'], '%Y-%m-%d')
    pub_date = data_obj.strftime('%a, %d %b %Y 11:00:00 GMT')

    # Caminho do arquivo de feed
    tree = ET.parse(caminho_feed)
    root = tree.getroot()
    channel = root.find('channel')

    # Verifica se o episódio já está no feed
    for item in channel.findall('item'):
        guid = item.find('guid')
        if guid is not None and arquivo_mp3 in guid.text:
            print("⚠️ Episódio já está no feed. Nada foi adicionado.")
            return

    # Cria novo item
    item = ET.Element('item')

    title_el = ET.SubElement(item, 'title')
    title_el.text = titulo

    desc_el = ET.SubElement(item, 'description')
    desc_el.text = descricao

    enclosure_el = ET.SubElement(item, 'enclosure', {
        'url': f'https://jonierthal.github.io/gol-de-algoritmo2/episodios/{arquivo_mp3}',
        'length': tamanho,
        'type': 'audio/mpeg'
    })

    guid_el = ET.SubElement(item, 'guid')
    guid_el.text = f'https://jonierthal.github.io/gol-de-algoritmo2/episodios/{arquivo_mp3}'

    pubdate_el = ET.SubElement(item, 'pubDate')
    pubdate_el.text = pub_date

    duration_el = ET.SubElement(item, 'itunes:duration')
    duration_el.text = duracao

    # Insere no topo da channel
    channel.insert(0, item)

    # Salva o feed atualizado
    ET.indent(tree, space="  ", level=0)
    tree.write(caminho_feed, encoding='utf-8', xml_declaration=True)
    print(f"✅ Episódio adicionado ao feed com sucesso: {arquivo_mp3}")
