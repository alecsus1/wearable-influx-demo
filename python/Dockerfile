FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir influxdb-client

COPY simulator.py .

CMD ["python", "simulator.py"]
