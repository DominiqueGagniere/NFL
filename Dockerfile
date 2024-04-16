FROM python:3.12.1-bullseye
WORKDIR /opt 
COPY templates/ /app/templates
COPY static/ /app/static
COPY nester.py /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install iputils-ping -y
RUN apt-get install postgresql-client -y 
CMD ["python", "./nester.py"]