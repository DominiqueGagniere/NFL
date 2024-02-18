FROM python:3.12.1-bullseye
WORKDIR /app
COPY templates/ /app/templates
COPY static/ /app/static
COPY nester.py /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install iputils-ping -y
CMD ["python", "./nester.py"]