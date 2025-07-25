import os
from lxml import etree
import json
from datetime import datetime

# Função para adicionar o episódio ao feed.xml
def adicionar_episodio_ao_feed(dados_episodio, channel, namespaces, base_url):
    item = etree.Element('item')

    # Adicionar as tags de dados no novo item
    title = etree.SubElement(item, 'title')
    title.text = dados_episodio['title']

    description = etree.SubElement(item, 'description')
    description.text = dados_episodio['description']

    # Verificar se a URL do áudio está presente e adicionar o URL completo
    if dados_episodio['audio_url']:
        audio_url_completo = base_url + dados_episodio['audio_url']
        
        # Adicionar o Enclosure com o URL completo
        enclosure = etree.SubElement(item, 'enclosure', {
            'url': audio_url_completo,
            'length': str(dados_episodio['audio_length']),
            'type': 'audio/mpeg'
        })
    else:
        print(f"Erro: áudio URL não fornecido para o episódio {dados_episodio['title']}.")
        return

    # Usar a URL completa do áudio como GUID
    guid = etree.SubElement(item, 'guid')
    guid.text = audio_url_completo

    pubDate = etree.SubElement(item, 'pubDate')
    pubDate.text = dados_episodio['pub_date'].strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Adicionar a duração do episódio com o namespace ns0
    ns0_duration = etree.SubElement(item, '{http://www.example.com/ns0}duration')  # Usando o namespace ns0
    ns0_duration.text = dados_episodio['duration']

    # Adicionar o item ao canal
    channel.append(item)

# Função para ler o JSON e retornar os dados
def obter_dados_episodio(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    if isinstance(dados, list):
        episodio = dados[0]
    else:
        episodio = dados

    return {
        'title': episodio.get('titulo', ''),
        'description': episodio.get('descricao', ''),
        'audio_url': episodio.get('arquivo', ''),
        'audio_length': episodio.get('tamanho', 0),
        'pub_date': datetime.strptime(episodio.get('data', ''), '%Y-%m-%d') if episodio.get('data') else None,
        'duration': episodio.get('duracao', '')
    }

# Função para verificar quais episódios já estão no XML
def obter_guids_existentes(xml_file, namespaces):
    # Carregar o arquivo XML
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Erro ao carregar o arquivo XML: {e}")
        return []

    # Verificar o XPath com o namespace correto
    channel = root.xpath('//atom:channel', namespaces=namespaces)[0]

    # Extrair todos os GUIDs (ou URLs) dos itens já existentes
    guids = [guid.text for guid in channel.xpath('.//guid', namespaces=namespaces)]
    
    return guids

# Função principal
def atualizar_feed():
    xml_file = 'rss/feed.xml'
    json_dir = 'roteiro/'  # Diretório onde os arquivos JSON estão armazenados

    # Definindo os namespaces corretamente
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',  # Namespace do Atom
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'ns2': 'https://podcastindex.org/namespace/1.0',
        'ns1': 'http://www.example.com/ns1'   # Namespace adicional
    }

    # Definir a URL base
    base_url = "https://jonierthal.github.io/gol-de-algoritmo2/episodios/"

    # Obter os GUIDs (ou URLs) dos episódios que já estão no feed
    guids_existentes = obter_guids_existentes(xml_file, namespaces)

    # Listar os arquivos JSON no diretório
    arquivos_json = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    # Carregar o arquivo XML
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Erro ao carregar o arquivo XML: {e}")
        return

    # Verificar o XPath com o namespace correto
    channel = root.xpath('//atom:channel', namespaces=namespaces)[0]

    # Obter a data de hoje
    hoje = datetime.today().strftime('%Y-%m-%d')

    # Iterar sobre os arquivos JSON e adicionar novos episódios
    for arquivo_json in arquivos_json:
        # Extrair a data do nome do arquivo
        data_episodio = arquivo_json.split('_')[1].replace('.json', '')

        # Adicionar o episódio do dia de hoje, mesmo que já exista
        if data_episodio == hoje or data_episodio not in guids_existentes:
            # Caminho do arquivo JSON
            json_file = os.path.join(json_dir, arquivo_json)

            # Obter os dados do episódio do arquivo JSON
            dados_episodio = obter_dados_episodio(json_file)

            # Adicionar o episódio ao feed
            adicionar_episodio_ao_feed(dados_episodio, channel, namespaces, base_url)
        else:
            print(f"Episódio de {data_episodio} já está no feed. Ignorando...")

    # Salvar as alterações no feed.xml
    try:
        tree.write(xml_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
        print("Novos episódios adicionados com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar o arquivo XML: {e}")

# Executar a função principal
atualizar_feed()
