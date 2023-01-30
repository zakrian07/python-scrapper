from typing import Union
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from Scrapper import Scrapper
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from typing import Set
import json


class BodyParam(BaseModel):
    parts: list[str]


scrapper = Scrapper()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Part Number Scrapper": "Welcome!"}


@app.get("/maxim/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Maxim(part_number)


@app.get("/omron/{part_number}")
def read_item(part_number):
    return scrapper.scrap_omron(part_number)


@app.get("/arrow/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Arrow(part_number)


@app.get("/molex/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Molex(part_number)


@app.post("/molexList")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_Molex, (part))
        futures.append(future)

    for future in futures:
        print(future.result())
        myList.append(future.result())
    return myList


async def get_body(request: Request):
    return await request.body()


@app.post("/molexs/")
def read_item(body: bytes = Depends(get_body)):
    partnumbers = json.loads(body)
    partnumbers = partnumbers['partnumbers']
    return scrapper.scrap_Molexs(partnumbers)


@app.get("/phoenix/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Phoenix(part_number)


@app.get("/rscomponents/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Rscomponents(part_number)


@app.get("/onsemi/{part_number}")
def read_item(part_number):
    return scrapper.scrap_onsemi(part_number)


@app.get("/mouser/{part_number}")
def read_item(part_number):
    return scrapper.scrap_mouser(part_number)


@app.get("/te/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Te(part_number)


@app.post("/teList")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_Te, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList
    # return scrapper.scrap_Te(part_number)


@app.get("/wago/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Wago(part_number)


@app.get("/findsupplier/{part_number}")
def read_item(part_number):
    return scrapper.find_Supplier(part_number)


@app.get("/scrap_3m/{part_number}")
def read_item(part_number):
    return scrapper.scrap_3m(part_number)


@app.get("/scrap_ti/{part_number}")
def read_item(part_number):
    return scrapper.scrap_ti(part_number)


@app.get("/scrap_murata/{part_number}")
def read_item(part_number):
    return scrapper.scrap_murata(part_number)


@app.get("/scrap_newark/{part_number}")
def read_item(part_number):
    return scrapper.scrap_newark(part_number)


@app.get("/scrap_festo/{part_number}")
def read_item(part_number):
    return scrapper.scrap_festo(part_number)
