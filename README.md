# ComplianceGrabber-2.0-archive

‣慂正湥 ⵤ਱
pip3 install -r requirements.txt
source scrapper/bin/activate
uvicorn main:app --host=0.0.0.0 --port=8000 --reload --timeout-keep-alive 9000000

OR
uvicorn main:app --host=0.0.0.0 --port=8080 --reload

ps aux | grep 'unicorn' | awk '{print $2}' | xargs sudo kill -9
uvicorn main:app --host=0.0.0.0 --port=8000 --reload
ps aux | grep unicorn
179 kill 29433
kill -QUIT 29433
kill -9 29433
killall unicorn

cd python-scrapper/

docker build -t pythonrestapi .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 818624402242.dkr.ecr.us-east-1.amazonaws.com
docker tag pythonrestapi:latest 818624402242.dkr.ecr.us-east-1.amazonaws.com/scrapper:v2
docker push 818624402242.dkr.ecr.us-east-1.amazonaws.com/scrapper:v2


 491  pgrep -a uvicorn
  492  kill 1278
  493  pip3  install -r requirements.txt 
  494  pgrep -a uvicorn
  495  nohup uvicorn main:app --host=0.0.0.0 --port=8000 --reload &
