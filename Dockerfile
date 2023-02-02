FROM python:3
RUN apt-get update && \
    apt-get install -y git
COPY . /action/
RUN cd /action && \
    pip install -r requirements.txt
CMD ["python", "/action/run.py"]
