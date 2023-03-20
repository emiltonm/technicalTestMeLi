FROM python:3.11.2

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip3 --no-cache-dir install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
