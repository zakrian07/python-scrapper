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
