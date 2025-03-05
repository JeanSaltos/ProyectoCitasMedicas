FROM python:3.9

# Instalar dependencias necesarias para ODBC y otros paquetes
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar el código y archivo de requerimientos
COPY backCitas.py requeriments.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requeriments.txt

# Exponer el puerto 5000 para acceder a la aplicación Flask
EXPOSE 5000

# Ejecutar el servidor Flask
CMD ["python", "backCitas.py"]
