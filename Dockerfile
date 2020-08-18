FROM python:3.6-stretch

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /main.py

RUN mkdir -p /input
VOLUME /input

RUN mkdir -p /output
VOLUME /output

ENTRYPOINT [ "python", "/main.py", "/input","/output" ]