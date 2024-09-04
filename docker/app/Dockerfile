FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    && apt-get clean

RUN git --version

RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

