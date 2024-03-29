FROM pypy:3.7-slim
RUN apt-get update && \
    apt-get install -y git watch
COPY . /action/
RUN cd /action && \
    pip install -r requirements.txt && \
    git config --global safe.directory '*'
CMD ["python", "/action/run.py"]
#CMD ["sleep", "infinity"]
