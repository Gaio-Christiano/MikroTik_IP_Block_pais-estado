# MikroTik_IP_Block_pais-estado
Programa em python que gera um relatório em Excel 2003 com base em uma lista de IP's bloqueados em regra de ScanPort (scaniamento de portas) no Mikrotik RB3011 e gera um relatório e informa os países e estados donde é o IP.



1.	Exportar a lista de IPs na lista PORTASCAN do Mikrotik.
2.	Identificar o local (origem) de cada IP (como o país ou cidade).
3.	Criar uma planilha Excel com colunas contendo:
o	IP
o	Data e Hora em que o IP foi adicionado à lista.
o	Origem do IP (país, cidade, etc.).
Vou detalhar o passo a passo para automatizar isso.
________________________________________
1. Exportar a lista de IPs com data/hora
No Mikrotik, use o seguinte comando para salvar a lista com IPs e horários em um arquivo:
/ip firewall address-list print file=portascan-list 
Isso cria um arquivo portascan-list.rsc no Mikrotik contendo informações como:
 Flags: X - disabled, D - dynamic
 #   LIST      ADDRESS         TIMEOUT
 0   PORTASCAN 192.168.1.1     1d
 1   PORTASCAN 203.0.113.10    3h
Transfira o arquivo para seu computador usando WinSCP ou FileZilla (modo SFTP). Caso precise de instruções para baixar o arquivo, posso detalhar.
________________________________________
2. Automatizar a Limpeza dos Dados
Você quer remover informações desnecessárias do arquivo para gerar um formato mais simples com IPs, datas e horários.
Se o arquivo for .rsc (como mostrado), você pode processar os dados em Python. Um script como este faz a limpeza:
python
Copiar código

import re
import requests
import pandas as pd

# Caminho do arquivo exportado do Mikrotik
file_path = "portascan-list.rsc"

# Expressão regular para extrair informações relevantes
pattern = r"(\d+\.\d+\.\d+\.\d+)\s+(\d{1,2}[a-z])?"

# Lista para armazenar os dados
data = []

with open(file_path, "r") as file:
    for line in file:
        match = re.search(pattern, line)
        if match:
            ip = match.group(1)
            timeout = match.group(2) if match.group(2) else "Unknown"
            # Adiciona à lista
            data.append({"IP": ip, "Timeout": timeout})

# Obter informações de localização para cada IP
for entry in data:
    ip = entry["IP"]
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    if response.status_code == 200:
        location = response.json().get("city", "Unknown") + ", " + response.json().get("country", "Unknown")
        entry["Location"] = location
    else:
        entry["Location"] = "Unknown"

# Criar um DataFrame do pandas
df = pd.DataFrame(data)

# Salvar como Excel
output_file = "Portascan_Report.xlsx"
df.to_excel(output_file, index=False)
print(f"Arquivo salvo em: {output_file}")
________________________________________
3. Explicação do Script
1.	Importação de bibliotecas:
o	re: Para processar o arquivo e extrair informações de IP.
o	requests: Para buscar a localização dos IPs usando a API do ipinfo.io.
o	pandas: Para criar e salvar a planilha Excel.
2.	Processamento:
o	Lê o arquivo exportado do Mikrotik.
o	Usa regex para identificar IPs e tempos de bloqueio.
o	Faz uma requisição para obter a localização de cada IP.
3.	Resultado:
o	Cria uma planilha Excel com as colunas IP, Timeout e Location.
________________________________________
4. Como Rodar o Script
1.	Instale as bibliotecas necessárias:
pip install pandas requests openpyxl

pip install requests

python -m pip install requests

python3 -m pip install requests

pip show requests

pip install pandas openpyxl

pip install xlwt

pip install requests

pip show requests

pip install pandas

python –version

where python

python limpeza.py
2.	Execute o script em Python.
3.	A planilha será salva como Portascan_Report.xlsx.
________________________________________
Se precisar de ajuda para rodar o script ou configurar algo, posso detalhar mais! 





import re
import requests
import pandas as pd

# Caminho do arquivo exportado do Mikrotik
file_path = "portascan-list.txt"

# Expressão regular para extrair informações relevantes (IP, data, hora e timeout)
pattern = r"PORTASCAN\s+([\d\.]+)\s+(\d{4}-\d{2}-\d{2})\s+([\d:]+)\s+([\d\w]+)"

# Lista para armazenar os dados
data = []

# Ler o arquivo e extrair IPs, data, hora e timeout
with open(file_path, "r") as file:
    for line in file:
        match = re.search(pattern, line)
        if match:
            ip = match.group(1)
            date = match.group(2)
            time = match.group(3)
            timeout = match.group(4)
            data.append({"IP": ip, "Date": date, "Time": time, "Timeout": timeout})

# Obter informações de localização para cada IP
for entry in data:
    ip = entry["IP"]
    try:
        # Requisição à API ipinfo.io
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if response.status_code == 200:
            json_data = response.json()
            city = json_data.get("city", "Unknown")
            country = json_data.get("country", "Unknown")
            entry["City"] = city
            entry["Country"] = country
        else:
            entry["City"] = "Unknown"
            entry["Country"] = "Unknown"
    except requests.exceptions.RequestException:
        entry["City"] = "Unknown"
        entry["Country"] = "Unknown"

# Criar um DataFrame do pandas
df = pd.DataFrame(data)

# Salvar como Excel
output_file = "Portascan_Report.xlsx"
df.to_excel(output_file, index=False)
print(f"Arquivo salvo em: {output_file}")


Como Funciona:
1.	Expressão Regular:
o	O padrão captura:
	IP: Sequência de números e pontos.
	Data: No formato AAAA-MM-DD.
	Hora: No formato HH:MM:SS.
	Timeout: O tempo restante para o IP permanecer bloqueado.
2.	Localização Geográfica:
o	Utiliza a API ipinfo.io para buscar a cidade e o país do IP.
3.	Saída:
o	Um arquivo Excel (Portascan_Report.xlsx) com as seguintes colunas:
	IP, Data, Hora, Timeout, Cidade, País.

