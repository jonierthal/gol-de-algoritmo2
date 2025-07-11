#coletar_noticias.py

# Importa as bibliotecas necessárias para fazer requisições HTTP e parsear o HTML
import requests
from bs4 import BeautifulSoup

# Função principal que faz a coleta das manchetes
def coletar_noticias_ge():
    # URL da seção de futebol do site ge.globo.com
    url = "https://ge.globo.com/futebol/"

    # Faz uma requisição GET para obter o conteúdo HTML da página
    response = requests.get(url)

    # Usa BeautifulSoup para interpretar o HTML retornado
    soup = BeautifulSoup(response.text, 'html.parser')

    # Lista que vai armazenar os títulos das notícias
    noticias = []

    # Busca todos os elementos <a> com a classe "feed-post-link", que contém os títulos
    #A classe CSS usada no GE para manchetes (feed-post-link) pode mudar no futuro. Se isso acontecer, é só ajustar o seletor CSS.
    for post in soup.select('a.feed-post-link'):
        # Extrai o texto do elemento <a>, removendo espaços em branco
        titulo = post.get_text(strip=True)

        # Verifica se o título é válido e se já coletamos menos de 5 manchetes
        if titulo and len(noticias) < 5:
            noticias.append(titulo)  # Adiciona à lista

    # Retorna a lista final com as 5 principais manchetes
    return noticias

# Executa este bloco se o script for rodado diretamente (e não importado como módulo)
if __name__ == "__main__":
    # Chama a função de coleta
    noticias = coletar_noticias_ge()

    # Imprime as manchetes numeradas
    for i, n in enumerate(noticias, 1):
        print(f"{i}. {n}")
