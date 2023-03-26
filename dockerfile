FROM python:3.10

WORKDIR /opt/app

COPY . .
COPY entrypoint.sh .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

#CMD [ "gunicorn", "main:app" ]
ENTRYPOINT ["sh", "entrypoint.sh"]