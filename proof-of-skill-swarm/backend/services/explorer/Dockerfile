FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN mkdir -p /app/proofs
VOLUME ["/app/proofs"]
EXPOSE 3013
CMD ["python", "app.py"]

