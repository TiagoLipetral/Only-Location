# Use a imagem oficial do Python com Debian Bullseye
FROM python:3.11-bullseye

# Atualiza repositórios para HTTPS e instala dependências necessárias, incluindo o driver ODBC da Microsoft
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y curl gnupg ca-certificates apt-transport-https software-properties-common \
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
 && apt-get install -y gcc g++ unixodbc unixodbc-dev libpq-dev libodbc1 \
 && ln -s /usr/lib/x86_64-linux-gnu/libodbc.so.2 /usr/lib/libodbc.so.2 \
 && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo requirements.txt e instala as dependências Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o container
COPY . .

# Comando para rodar sua aplicação
CMD ["python", "main.py"]
