import requests
from bs4 import BeautifulSoup
import os

url = "https://genshin-impact.fandom.com/wiki/Local_Specialty"
diretorio_destino = "icons_local_specialty"

# Cria o diretório de destino se não existir
if not os.path.exists(diretorio_destino):
    os.makedirs(diretorio_destino)

try:
    response = requests.get(url)
    response.raise_for_status() # Lança uma exceção para status de erro (4xx ou 5xx)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontra as tabelas que contêm as especialidades por região
    # Pode ser necessário ajustar o seletor CSS dependendo da estrutura exata da página
    # Com base no conteúdo da página, parece que as tabelas estão dentro de divs com a classe 'mw-parser-output'
    # e são as tabelas que contêm as listas de especialidades por região.
    # Vamos tentar encontrar as tabelas que estão logo após os cabeçalhos de região (h3)
    
    regioes = ['Mondstadt', 'Liyue', 'Inazuma', 'Sumeru', 'Fontaine', 'Natlan']
    
    for regiao in regioes:
        # Encontra o cabeçalho da região
        heading = soup.find('span', id=regiao)
        if heading:
            # Encontra a tabela que geralmente segue o cabeçalho da região
            # Isso pode variar, então pode precisar de ajuste fino
            table = heading.find_parent().find_next_sibling('table')
            
            if table:
                # Itera sobre as linhas da tabela (ignorando o cabeçalho se houver)
                for row in table.find_all('tr')[1:]:
                    # Encontra as células da linha
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        # A primeira célula geralmente contém a imagem e a segunda o nome
                        img_tag = cells[0].find('img')
                        name_tag = cells[1].find('a')
                        
                        if img_tag and name_tag:
                            image_url = img_tag.get('data-src') or img_tag.get('src')
                            item_name = name_tag.get_text(strip=True)
                            
                            if image_url and item_name:
                                # Formata o nome para ser um nome de arquivo válido
                                nome_arquivo = f"{item_name.replace(' ', '_').replace('/', '_')}.png"
                                caminho_completo = os.path.join(diretorio_destino, nome_arquivo)
                                
                                try:
                                    # Baixa a imagem
                                    print(f'Baixando {item_name}...')
                                    imagem_response = requests.get(image_url, stream=True)
                                    imagem_response.raise_for_status()
                                    
                                    with open(caminho_completo, 'wb') as f:
                                        for chunk in imagem_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    print(f'Salvo como {nome_arquivo}')
                                    
                                except requests.exceptions.RequestException as e:
                                    print(f'Erro ao baixar {item_name} ({image_url}): {e}')
                                except Exception as e:
                                    print(f'Erro ao salvar {item_name}: {e}')

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a página: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
