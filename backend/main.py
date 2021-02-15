from typing import Optional
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
import requests
import time
import uvicorn
from uptime import uptime, boottime

app = FastAPI()

defaultEnv = {
    "_BACKEND_SERVICE": "http://" + "backend-service",
    "_FRONTEND_SERVICE": "http://" + "frontend-service",
    "_DB_SERVICE": "http://" + "db-service",
    "_DEFAULT_SLEEP": 1,
    "_INCREMENTAL_SLEEP": 2
}


def getEnvVar(envVar):
    if envVar not in os.environ:
        return defaultEnv[envVar]
    else:
        return os.environ[envVar]


@app.get("/")
def baseUrl():
    return {"Microservice": "BackEnd"}


@app.get("/roundtrip")
def roundTrip():
    destination_api = getEnvVar("_DB_SERVICE") + "/roundtrip"
    print("destination_api: ", destination_api)
    try:
        response = requests.get(destination_api, verify=False)
    except requests.exceptions.RequestException as e:
        print("ERROR: Internal Service Error", "\n", "ERROR_DETAILS:", e)
        return JSONResponse(status_code=500, content={"Error": "Internal Service Error"})

    if response.status_code != 200:
        print("ResponseCode:", response.status_code)
        print("Error: ", response.text)
        return JSONResponse(status_code=response.status_code,
                            content={"Error": "From: " + destination_api + " ReturnCode: " + str(response.status_code)})

    return JSONResponse(status_code=response.status_code,
                        content={"response": response.json(), "ReturnCode": response.status_code})
    

@app.get("/failedflow")
def failedFlow():
    return JSONResponse(status_code=500,
                        content={"response": "Returning default code 500 from BackEnd Service",
                                 "ReturnCode": 500})


@app.get("/dbquery")
def slowDb():
    destination_api = getEnvVar("_DB_SERVICE") + "/dbquery"
    print("destination_api: ", destination_api)
    try:
        response = requests.get(destination_api, verify=False)
    except requests.exceptions.RequestException as e:
        print("ERROR: Internal Service Error", "\n", "ERROR_DETAILS:", e)
        return JSONResponse(status_code=500, content={"Error": "Internal Service Error"})

    if response.status_code != 200:
        print("ResponseCode:", response.status_code)
        print("Error: ", response.text)
        return JSONResponse(status_code=response.status_code,
                            content={"Error": "From: " + destination_api + " ReturnCode: " + str(response.status_code)})

    return JSONResponse(status_code=response.status_code,
                        content={"response": response.json(), "ReturnCode": response.status_code})


@app.get("/slowdb")
def slowDb():
    destination_api = getEnvVar("_DB_SERVICE") + "/slowdbquery"
    print("destination_api: ", destination_api)
    try:
        response = requests.get(destination_api, verify=False)
    except requests.exceptions.RequestException as e:
        print("ERROR: Internal Service Error", "\n", "ERROR_DETAILS:", e)
        return JSONResponse(status_code=500, content={"Error": "Internal Service Error"})

    if response.status_code != 200:
        print("ResponseCode:", response.status_code)
        print("Error: ", response.text)
        return JSONResponse(status_code=response.status_code,
                            content={"Error": "From: " + destination_api + " ReturnCode: " + str(response.status_code)})

    return JSONResponse(status_code=response.status_code,
                        content={"response": response.json(), "ReturnCode": response.status_code})


@app.get("/sleep/{seconds}")
def sleep(seconds: int):
    destination_api = getEnvVar("_DB_SERVICE") + "/sleep"
    print("destination_api: ", destination_api)
    if not 0 <= seconds <= 10:
        seconds = defaultEnv["_DEFAULT_SLEEP"]

    sleep_seconds = seconds + getEnvVar("_INCREMENTAL_SLEEP")
    print("Sleeping for : {} seconds".format(sleep_seconds))
    time.sleep(sleep_seconds)

    try:
        response = requests.get(destination_api + "/" + str(sleep_seconds), verify=False)
    except requests.exceptions.RequestException as e:
        print("ERROR: Internal Service Error", "\n", "ERROR_DETAILS:", e)
        return JSONResponse(status_code=500, content={"Error": "Internal Service Error"})

    if response.status_code != 200:
        print("ResponseCode:", response.status_code)
        print("Error: ", response.text)
        return JSONResponse(status_code=response.status_code,
                            content={"Error": "From: " + destination_api + " ReturnCode: " + str(response.status_code)})

    return JSONResponse(status_code=response.status_code,
                        content={"response": response.json(), "ReturnCode": response.status_code})


@app.get("/health")
def returnHealth():
    health_status = {"Status": "OK",
                     "uptime": jsonable_encoder(uptime()),
                     "boottime": jsonable_encoder(boottime())
                     }
    return JSONResponse(status_code=200, content=health_status)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
