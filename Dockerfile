# app/Dockerfile

FROM python:3.10-slim

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    libmariadb-dev\
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/kd9lsv/contester_master_dashboard.git .

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "main_board.py", "--server.port=8501", "--server.address=0.0.0.0"]