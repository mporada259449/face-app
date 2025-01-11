FROM python:3.11

COPY app requirements.txt /face-app/
WORKDIR /face-app
RUN pip3 install -r requirements.txt

CMD [ "flask", "--app", ".", "run", "-h", "0.0.0.0", "-p", "8000" ]

