FROM python:3.8-slim

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY util.py .
COPY STOCK_001.py .
COPY STOCK_002.py .
COPY STOCK_003_HK.py .
COPY STOCK_004_HK.py .
COPY SPXOPTION_001.py .

# no entry point
# ENTRYPOINT ["python","/app/consumer.py"]