FROM python:3.9.6-slim-buster
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /jsonstorage
COPY . /jsonstorage
RUN pip3 install -r requirements.txt
CMD ["python3","theserver.py"]
