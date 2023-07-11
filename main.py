from typing import Union
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from Scrapper import Scrapper
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from typing import Set
import json
import asyncio
# from distributors.rshughes import scrap_rshughes
# from distributors.sager import scrap_sager


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
    partnumber = part_number.replace("/", "")
    return scrapper.scrap_Arrow(partnumber)


@app.get("/molex/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Molex(part_number)


@app.post("/molexList_old")
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


@app.get("/molexList/{part_number}")
def read_item(part_number):
    return scrapper.scrap_Molex(part_number)


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
    part_number = part_number.replace('qr', '/')
    print(part_number)
    return scrapper.scrap_ti(part_number)


@app.get("/scrap_murata/{part_number}")
def read_item(part_number):
    return scrapper.scrap_murata(part_number)


@app.post("/scrap_murata_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_murata, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_newark/{part_number}")
def read_item(part_number):
    return scrapper.scrap_newark(part_number)


@app.get("/scrap_festo/{part_number}")
def read_item(part_number):
    return scrapper.scrap_festo(part_number)


@app.get("/scrap_fair_rite/{part_number}")
async def read_item(part_number):
    return scrapper.scrap_fair_rite(part_number)


@app.post("/scrap_fair_rite_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    print("scrap_fair_rite====", scrapper.scrap_fair_rite)
    for part in body.parts:
        future = executor.submit(scrapper.scrap_fair_rite, (part))
        print("future", future)
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get('/scrap_panduit/{part_number}')
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_panduit(part_number)


# @app.get('/scrap_alphawire/{part_number}')
# def read_item(part_number):
#     return scrapper.scrap_alphawire(part_number)


# @app.post("/scrap_alphawire_list")
# def read_item(body: BodyParam):
#     print("body", body.parts)
#     myList = []
#     executor = ThreadPoolExecutor()
#     futures = []

#     for part in body.parts:
#         print("part:", part)
#         future = executor.submit(scrapper.scrap_alphawire, (part))
#         print("future", future)
#         futures.append(future)

#     for future in futures:
#         myList.append(future.result())
#     return myList


@app.get('/scrap_analog/{part_number}')
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_analog(part_number)


@app.post("/scrap_analog_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []

    for part in body.parts:
        future = executor.submit(scrapper.scrap_analog, (part))
        print("future", future)
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_tdk/{part_number}")
def read_item(part_number):
    return scrapper.scrap_tdk(part_number)


@app.post("/scrap_tdk_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []

    for part in body.parts:
        future = executor.submit(scrapper.scrap_tdk, (part))
        print("future", future)
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_microchip/{part_number}")
def read_item(part_number):
    return scrapper.scrap_microchip(part_number)


@app.post("/scrap_microchip_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_microchip, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_allegro/{part_number}")
def read_item(part_number):
    return scrapper.scrap_allegro(part_number)


@app.post("/scrap_allegro_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_allegro, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_yageo/{part_number}")
def read_item(part_number):
    return scrapper.scrap_yageo(part_number)


@app.post("/scrap_yageo_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_yageo, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_leespring/{part_number}")
def read_item(part_number):
    return scrapper.scrap_leespring(part_number)


@app.post("/scrap_leespring_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_leespring, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrape_mcmaster/{part_number}")
def read_item(part_number):
    return scrapper.scrape_mcmaster(part_number)


@app.post("/scrape_mcmaster_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        try:
            future = executor.submit(scrapper.scrape_mcmaster, (part))
            futures.append(future)
        except Exception as exc:
            futures.append(exc)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_abracon/{part_number}")
def read_item(part_number):
    return scrapper.scrap_abracon(part_number)


@app.post("/scrap_abracon_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_abracon, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_panasonic/{part_number}")
def read_item(part_number):
    return scrapper.scrap_panasonic(part_number)


@app.post("/scrap_panasonic_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_panasonic, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList
# @app.get("/scrap_sager/{part_number}")
# def read_item(part_number):
#     return scrap_sager(part_number)


# @app.post("/scrap_sager_list")
# def read_item(body: BodyParam):
#     print("body", body.parts)
#     myList = []
#     executor = ThreadPoolExecutor()
#     futures = []
#     for part in body.parts:
#         future = executor.submit(scrapper.scrap_sager, (part))
#         futures.append(future)

#     for future in futures:
#         myList.append(future.result())
#     return myList


@app.get("/scrap_vishay/{part_number}")
def read_item(part_number):
    return scrapper.scrap_vishay(part_number)


@app.post("/scrap_vishay_list")
def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_vishay, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
        print(myList)
    return myList


@app.get("/scrap_alliedelectronics/{part_number}")
def read_item(part_number):
    return scrapper.scrap_alliedelectronics(part_number)


@app.post("/scrap_alliedelectronics_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_alliedelectronics, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_pemnet/{part_number}")
def read_item(part_number):
    return scrapper.scrap_pemnet(part_number)


@app.post("/scrap_pemnet_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_pemnet, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_belfuse/{part_number}")
def read_item(part_number):
    return scrapper.scrap_belfuse(part_number)


@app.post("/scrap_belfuse_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_belfuse, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_radiall/{part_number}")
def read_item(part_number):
    return scrapper.scrap_radiall(part_number)


@app.post("/scrap_radiall_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_radiall, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_semtech/{part_number}")
def read_item(part_number):
    return scrapper.scrap_semtech(part_number)


@app.post("/scrap_semtech_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_semtech, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_yuden/{part_number}")
def read_item(part_number):
    return scrapper.scrap_yuden(part_number)


@app.post("/scrap_yuden_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_yuden, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_alphawire/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_alphawire(part_number)


@app.post("/scrap_alphawire_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_alphawire, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_tti/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_tti(part_number)


@app.post("/scrap_tti_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_tti, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_infineon/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_infineon(part_number)


@app.post("/scrap_infineon_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_infineon, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrape_bivar/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_bivar(part_number)


@app.post("/scrape_bivar_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrape_bivar, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrape_st/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_st(part_number)


@app.post("/scrape_st_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(executor, scrapper.scrape_st, part)
        result = await future
        myList.append(result)

    return myList

# scrape_avnet


@app.get("/scrape_avnet/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_avnet(part_number)


@app.post("/scrape_avnet_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(executor, scrapper.scrape_avnet, part)
        result = await future
        myList.append(result)

    return myList

# scrape_distrelec


@app.get("/scrape_distrelec/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_distrelec(part_number)


@app.post("/scrape_distrelec_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(
            executor, scrapper.scrape_distrelec, part)
        result = await future
        myList.append(result)

    return myList

# scrape_harwin


@app.get("/scrape_harwin/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_harwin(part_number)


@app.post("/scrape_harwin_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(executor, scrapper.scrape_harwin, part)
        result = await future
        myList.append(result)

    return myList


@app.get("/scrape_boeing/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_boeing(part_number)


@app.post("/scrape_boeing_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(executor, scrapper.scrape_boeing, part)
        result = await future
        myList.append(result)

    return myList

# scrape_harwin


@app.get("/scrape_index_corp/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_index_corp(part_number)


@app.post("/scrape_index_corp_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    for part in body.parts:
        future = loop.run_in_executor(
            executor, scrapper.scrape_index_corp, part)
        result = await future
        myList.append(result)

    return myList


@app.get("/scrape_skywork/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_skywork(part_number)


@app.post("/scrape_skywork_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrape_skywork, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrap_sager/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrap_sager(part_number)


@app.post("/scrap_sager_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrap_sager, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList


@app.get("/scrape_littelfuse/{part_number:path}")
def read_item(part_number):
    print(part_number)
    return scrapper.scrape_littelfuse(part_number)


@app.post("/scrape_littelfuse_list")
async def read_item(body: BodyParam):
    print("body", body.parts)
    myList = []
    executor = ThreadPoolExecutor()
    futures = []
    for part in body.parts:
        future = executor.submit(scrapper.scrape_littelfuse, (part))
        futures.append(future)

    for future in futures:
        myList.append(future.result())
    return myList
# @app.get("/scrap_rshughes/{part_number}")
# def read_item(part_number):
#     return scrap_rshughes(part_number)


# @app.post("/scrap_rshughes_list")
# def read_item(body: BodyParam):
#     print("body", body.parts)
#     myList = []
#     executor = ThreadPoolExecutor()
#     futures = []
#     for part in body.parts:
#         future = executor.submit(scrapper.scrap_rshughes, (part))
#         futures.append(future)

#     for future in futures:
#         myList.append(future.result())
#     return myList
