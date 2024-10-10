FROM python:3.9-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# RUN apt-get update && apt-get install -y bash
ENTRYPOINT [ "python3", "mpskit" ]