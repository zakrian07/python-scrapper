# ComplianceGrabber-2.0-archive
‣慂正湥ⵤ਱

source scrapper/bin/activate

uvicorn main:app --host=0.0.0.0 --port=8000 --reload

  ps aux | grep 'unicorn' | awk '{print $2}' | xargs sudo kill -9
  176  history
  177  uvicorn main:app --host=0.0.0.0 --port=8000 --reload
  178  ps aux | grep unicorn
  179  kill 29433
  180  kill 7004
  181  kill 2052
  182  kill -QUIT 29433
  183  kill -QUIT 7004
  184  kill -9 7004
  185  kill -9 29433
  186  killall unicorn
  187  sudo reboot 
  188  ls
  189  cd python-scrapper/
uvicorn main:app --host=0.0.0.0 --port=8000 --reload  --timeout-keep-alive 90000