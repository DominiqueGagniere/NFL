FROM python:3.12.1-bullseye
WORKDIR /app
COPY harvester.py /app/
COPY requirements.txt /app/
COPY ping_nmap.py /app/
COPY scan_result.json /app/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install iputils-ping -y
CMD ["python", "./harvester.py"]