FROM python:3.12.1-bookworn
WORKDIR /app
COPY . /app
RUN pip install -r requirement.txt
CMD [“python”, “./app.py”]
