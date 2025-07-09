import re # Módulo para expressões regulares, usado para extrair informações das linhas do log.
import pandas as pd # Biblioteca para manipulação e análise de dados, usada para criar DataFrames e exportar para Excel.
from datetime import datetime # Módulo para trabalhar com datas e horas, usado para nomear o arquivo de saída.
from time import sleep # Módulo para pausar a execução, usado para controlar o ritmo das requisições a APIs.
import requests # Módulo para fazer requisições HTTP, usado para consultar as APIs de geolocalização.
import os # Módulo para interagir com o sistema operacional, usado para verificar a existência do arquivo.

# --- Configurações Iniciais ---

# Caminho do arquivo exportado do Mikrotik contendo os logs de portscan.
# Certifique-se de que este arquivo esteja no mesmo diretório do script
# ou forneça o caminho completo para ele.
file_path = "portascan-list.txt"

# Verificar se o arquivo de entrada existe antes de prosseguir com a leitura.
if not os.path.exists(file_path):
    print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    # Sair do script se o arquivo não for encontrado para evitar erros futuros.
    exit()

# Expressão regular para extrair informações da linha de log do Mikrotik.
# O padrão busca por:
# 1. "PORTASCAN " (texto literal)
# 2. ([\d\.]+) - Captura o endereço IP (grupo 1: um ou mais dígitos/pontos).
# 3. \s+ - Um ou mais espaços em branco.
# 4. (\d{4}-\d{2}-\d{2}) - Captura a data no formato AAAA-MM-DD (grupo 2).
# 5. \s+ - Um ou mais espaços em branco.
# 6. ([\d:]+) - Captura a hora no formato HH:MM:SS (grupo 3).
# 7. (?:\s+([\d\w]+))? - Grupo não capturante (?:...) que significa que o conteúdo é opcional (?...).
#    \s+ - Um ou mais espaços em branco.
#    ([\d\w]+) - Captura o Timeout (grupo 4: um ou mais dígitos/letras), se presente.
pattern = r"PORTASCAN\s+([\d\.]+)\s+(\d{4}-\d{2}-\d{2})\s+([\d:]+)(?:\s+([\d\w]+))?"

# Lista para armazenar os dados de cada entrada de log após a extração.
dados = []

# --- Leitura e Validação do Arquivo ---

# Abrir o arquivo no modo de leitura ('r'). O 'with' garante que o arquivo seja fechado automaticamente.
with open(file_path, "r") as arquivo:
    # Iterar sobre cada linha do arquivo.
    for linha in arquivo:
        # Tentar encontrar o padrão da expressão regular na linha atual.
        match = re.search(pattern, linha)
        if match:
            # Se houver correspondência, extrair os grupos capturados.
            ip = match.group(1)
            data = match.group(2)
            hora = match.group(3)
            # O timeout é opcional; se o grupo 4 não for encontrado, define como "Sem Timeout".
            timeout = match.group(4) if match.group(4) else "Sem Timeout"
            # Adicionar um dicionário com os dados extraídos à lista 'dados'.
            # Inicializamos 'Provedor' e 'Email Provedor' com valores padrão.
            dados.append({
                "IP": ip,
                "Data": data,
                "Hora": hora,
                "Timeout": timeout,
                "Provedor": "Desconhecido", # Novo campo para o nome do provedor, inicializado.
                "Email Provedor": "Não disponível via API de Geolocalização" # Novo campo para e-mail, com nota.
            })
        else:
            # Se a linha não corresponder ao formato esperado, ela é ignorada e uma mensagem de aviso é impressa.
            print(f"Linha ignorada (formato inválido): {linha.strip()}")

# Verificar se algum dado válido foi encontrado e processado no arquivo.
if not dados:
    print("Erro: Nenhum dado válido foi encontrado no arquivo.")
    # Sair do script se não houver dados para processar.
    exit()

# --- Funções para Consultar Múltiplas APIs de Geolocalização ---

# Função para consultar a API ipwhois.app (agora ipwhois.io).
# Retorna Cidade, Estado, País, CEP e Provedor.
def consultar_geolocalizacao_api1(ip):
    try:
        # Faz uma requisição GET para a API ipwhois.app com o IP fornecido.
        # Define um timeout de 10 segundos para a requisição para evitar travamentos.
        response = requests.get(f"https://ipwhois.app/json/{ip}", timeout=10)
        # Verifica se a requisição foi bem-sucedida (código de status HTTP 200).
        if response.status_code == 200:
            # Converte a resposta JSON da API em um dicionário Python.
            data = response.json()
            # Retorna os campos relevantes, usando "Desconhecida" se o campo não existir.
            # O campo 'isp' contém o nome do provedor.
            return (
                data.get("city", "Desconhecida"),
                data.get("region", "Desconhecida"),
                data.get("country", "Desconhecido"),
                data.get("zip", "Desconhecido"),
                data.get("isp", "Desconhecido"), # Extrai o nome do provedor (ISP)
            )
    except Exception as e:
        # Em caso de qualquer erro (conexão, JSON inválido, etc.), imprime uma mensagem de erro.
        print(f"Erro na API 1 (ipwhois.app) para {ip}: {e}")
    # Retorna valores padrão "Desconhecido" para todos os campos em caso de falha.
    return "Desconhecida", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecido"

# Função para consultar a API ipstack.com.
# Requer uma chave de API (access_key) para funcionar.
def consultar_geolocalizacao_api2(ip):
    try:
        # ATENÇÃO: Substitua "SUA_CHAVE_DE_API" pela sua chave de API real do ipstack.com.
        # Sem uma chave válida, esta API não funcionará corretamente ou retornará erros.
        access_key = "SUA_CHAVE_DE_API" # <-- SUBSTITUA PELA SUA CHAVE DE API
        # Faz uma requisição GET para a API ipstack.com.
        response = requests.get(f"http://api.ipstack.com/{ip}?access_key={access_key}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # ipstack pode ter o ISP em 'connection.isp' ou 'organization'. Tentamos ambos.
            isp_name = data.get("connection", {}).get("isp", data.get("organization", "Desconhecido"))
            return (
                data.get("city", "Desconhecida"),
                data.get("region_name", "Desconhecida"),
                data.get("country_name", "Desconhecido"),
                data.get("zip", "Desconhecido"),
                isp_name,
            )
    except Exception as e:
        print(f"Erro na API 2 (ipstack.com) para {ip}: {e}")
    return "Desconhecida", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecido"

# Função para consultar a API ip-api.com.
# Esta API é geralmente gratuita para uso não comercial e não requer uma chave de API.
def consultar_geolocalizacao_api3(ip):
    try:
        # Faz uma requisição GET para a API ip-api.com, solicitando explicitamente os campos necessários.
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=city,regionName,country,zip,isp,org", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # ip-api.com pode retornar o nome do provedor no campo 'isp' ou 'org'. Priorizamos 'isp'.
            isp_name = data.get("isp", data.get("org", "Desconhecido"))
            return (
                data.get("city", "Desconhecida"),
                data.get("regionName", "Desconhecida"),
                data.get("country", "Desconhecido"),
                data.get("zip", "Desconhecido"),
                isp_name,
            )
    except Exception as e:
        print(f"Erro na API 3 (ip-api.com) para {ip}: {e}")
    return "Desconhecida", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecido"

# Função principal para consultar geolocalização de um IP, tentando várias APIs em sequência.
# Itera pelas funções de consulta até encontrar um resultado válido (onde o País não é "Desconhecido").
def consultar_geolocalizacao(ip):
    # Lista de funções de API a serem tentadas. A ordem pode ser ajustada conforme a preferência.
    for consulta in [consultar_geolocalizacao_api1, consultar_geolocalizacao_api2, consultar_geolocalizacao_api3]:
        # Tenta consultar a API e desempacota os resultados em variáveis.
        cidade, estado, pais, cep, provedor = consulta(ip)
        # Se o país não for "Desconhecido", consideramos que a consulta foi bem-sucedida para este IP.
        if pais != "Desconhecido":
            # Retorna os dados encontrados pela primeira API bem-sucedida.
            return cidade, estado, pais, cep, provedor
    # Se todas as APIs falharem em fornecer dados válidos para o país, retorna valores padrão.
    return "Desconhecida", "Desconhecida", "Desconhecido", "Desconhecido", "Desconhecido"

# --- Processamento dos IPs e Busca de Geolocalização ---

# Iterar sobre cada entrada de IP na lista 'dados' para enriquecer com informações de geolocalização.
# 'enumerate' é usado para obter o índice (idx) e o valor (entrada) de cada item.
for idx, entrada in enumerate(dados, start=1):
    ip = entrada["IP"]
    # Imprimir o progresso do processamento.
    print(f"Processando IP {idx}/{len(dados)}: {ip}")
    # Chamar a função principal de geolocalização para o IP atual.
    cidade, estado, pais, cep, provedor = consultar_geolocalizacao(ip)
    # Atualizar o dicionário 'entrada' com as informações obtidas das APIs.
    entrada["Cidade"] = cidade
    entrada["Estado"] = estado
    entrada["País"] = pais
    entrada["CEP"] = cep
    entrada["Provedor"] = provedor # Adiciona o nome do provedor
    # 'Província' e 'Bairro' são mapeados para 'Estado' e 'Cidade' para compatibilidade ou granularidade.
    entrada["Província"] = estado
    entrada["Bairro"] = cidade if cidade != "Desconhecida" else "Desconhecido"
    # Pausar a execução por 1 segundo entre as requisições. Isso é crucial para
    # não exceder os limites de taxa de requisições impostos pelas APIs gratuitas/freemium.
    sleep(1)

# --- Criação do DataFrame e Geração de Relatórios ---

# Criar um DataFrame do pandas a partir da lista de dicionários 'dados'.
# Este DataFrame será a base para todos os relatórios.
df = pd.DataFrame(dados)

# Resumo por País: Agrupa os dados por 'País' e calcula a quantidade de IPs,
# o número de estados únicos e o número de cidades únicas em cada país.
resumo_pais = (
    df.groupby("País")
    .agg(
        Quantidade=("País", "size"), # Conta o número de ocorrências de cada país.
        Estados_Uniquos=("Estado", lambda x: len(set(x))), # Conta estados únicos dentro de cada país.
        Cidades_Uniquas=("Cidade", lambda x: len(set(x))), # Conta cidades únicas dentro de cada país.
    )
    .reset_index() # Transforma o índice 'País' de volta em uma coluna.
)

# Estados por País: Agrupa os dados por 'País' e 'Estado' e conta a quantidade de IPs em cada estado.
estados_por_pais = (
    df.groupby(["País", "Estado"])
    .agg(Quantidade=("Estado", "size")) # Conta o número de IPs para cada combinação de País e Estado.
    .reset_index()
)

# Bairros por Estado e País: Agrupa os dados por 'País', 'Estado' e 'Bairro' e conta a quantidade de IPs.
bairros_por_estado_pais = (
    df.groupby(["País", "Estado", "Bairro"])
    .agg(Quantidade=("Bairro", "size")) # Conta o número de IPs para cada combinação de País, Estado e Bairro.
    .reset_index()
)

# NOVO: Resumo por Provedor: Agrupa os dados por 'Provedor' e conta a quantidade de IPs.
# Também tenta listar e-mails únicos, embora a maioria será "Não disponível..."
resumo_provedor = (
    df.groupby("Provedor")
    .agg(
        Quantidade=("Provedor", "size"), # Conta o número de IPs para cada provedor.
        # Coleta e-mails únicos, filtrando os valores padrão de "Não disponível...".
        Emails_de_Contato=("Email Provedor", lambda x: ", ".join(sorted(set(e for e in x if e != "Não disponível via API de Geolocalização" and e != "Desconhecido"))))
    )
    .reset_index()
)
# Renomear a coluna de e-mails para algo mais claro no relatório.
resumo_provedor.rename(columns={"Emails_de_Contato": "Emails de Contato (se disponível)"}, inplace=True)


# Calcular o total de IPs para usar nos cálculos de porcentagem.
total_ips = len(df)

# Porcentagem por País: Calcula o percentual de IPs para cada país em relação ao total.
porcentagem_pais = (
    df.groupby("País")
    .agg(Quantidade=("País", "size"))
    .assign(Percentual=lambda x: (x["Quantidade"] / total_ips) * 100) # Adiciona uma nova coluna 'Percentual'.
    .reset_index()
)

# Porcentagem por Estado: Calcula o percentual de IPs para cada estado em relação ao total.
porcentagem_estado = (
    df.groupby(["País", "Estado"])
    .agg(Quantidade=("Estado", "size"))
    .assign(Percentual=lambda x: (x["Quantidade"] / total_ips) * 100)
    .reset_index()
)

# NOVO: Porcentagem por Provedor: Calcula o percentual de IPs para cada provedor em relação ao total.
porcentagem_provedor = (
    df.groupby("Provedor")
    .agg(Quantidade=("Provedor", "size"))
    .assign(Percentual=lambda x: (x["Quantidade"] / total_ips) * 100)
    .reset_index()
)

# Resumo de localização: Mostra a porcentagem de IPs com informações localizadas para cada campo.
# Inclui o campo "Provedor" neste resumo.
colunas = ["Cidade", "Estado", "País", "CEP", "Provedor"] # Adicionado "Provedor"
localizacao_resumo = {
    "Coluna": colunas,
    "Localizados (%)": [
        # Calcula a porcentagem de IPs onde o valor do campo NÃO é "Desconhecida" ou "Não disponível...".
        100 - ((df[coluna].isin(["Desconhecida", "Não disponível via API de Geolocalização"])).sum() / total_ips * 100) for coluna in colunas
    ],
}
df_localizacao_resumo = pd.DataFrame(localizacao_resumo)

# --- Salvando o Relatório em Excel ---

# Gerar o nome do arquivo de saída com o carimbo de data e hora atual para garantir unicidade.
hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
arquivo_saida = f"10G Relatorio_Completo_PortaScan_{hora_atual}.xlsx"

# Salvar todos os DataFrames em abas diferentes no mesmo arquivo Excel.
# O 'engine="openpyxl"' é necessário para permitir a escrita em múltiplas planilhas (sheets).
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Detalhes_IPs", index=False) # Aba com todos os detalhes dos IPs e suas localizações.
    resumo_pais.to_excel(writer, sheet_name="Resumo por País", index=False) # Resumo da distribuição de IPs por país.
    estados_por_pais.to_excel(writer, sheet_name="Estados por País", index=False) # Distribuição de IPs por estado dentro de cada país.
    bairros_por_estado_pais.to_excel(writer, sheet_name="Bairros por Estado e País", index=False) # Distribuição de IPs por bairro/cidade.
    resumo_provedor.to_excel(writer, sheet_name="Resumo por Provedor", index=False) # NOVO: Resumo da distribuição de IPs por provedor.
    porcentagem_pais.to_excel(writer, sheet_name="Porcentagem por País", index=False) # Percentual de IPs por país.
    porcentagem_estado.to_excel(writer, sheet_name="Porcentagem por Estado", index=False) # Percentual de IPs por estado.
    porcentagem_provedor.to_excel(writer, sheet_name="Porcentagem por Provedor", index=False) # NOVO: Percentual de IPs por provedor.
    df_localizacao_resumo.to_excel(writer, sheet_name="Resumo de Localização", index=False) # Resumo da completude dos dados de localização.

print(f"Relatório salvo com sucesso em: {arquivo_saida}")
print("\n--- Informação Importante sobre 'Email Provedor' ---")
print("As APIs de geolocalização gratuitas/freemium utilizadas neste script (ipwhois.app, ipstack.com, ip-api.com) geralmente não fornecem o e-mail de contato do provedor (comumente chamado de 'abuse contact').")
print("Essa informação é tipicamente obtida através de consultas WHOIS, que são um processo diferente do lookup de geolocalização.")
print("Consultas WHOIS podem ter suas próprias limitações de taxa de requisições e exigem um tratamento mais complexo para extração de dados em massa.")
print("Para obter e-mails de contato de provedores de forma confiável e em escala para fins de denúncia, você precisaria integrar uma API WHOIS específica ou usar bibliotecas Python dedicadas a WHOIS lookups (ex: 'python-whois') e lidar com as políticas de uso dessas fontes.")