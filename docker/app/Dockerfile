FROM python:3.8


RUN apt-get update && apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && apt-get clean

RUN git --version

RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

