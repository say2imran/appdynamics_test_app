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
    "_INCREMENTAL_SLEEP": 1
}


def getEnvVar(envVar):
    if envVar not in os.environ:
        print("WARNING: OS Env: {} not found, using defaultEnv Value".format(envVar))
        return defaultEnv[envVar]
    else:
        return os.environ[envVar]


@app.get("/")
def baseUrl():
    return {"Microservice": "FrontEnd"}


@app.get("/roundtrip")
def roundTrip():
    destination_api = getEnvVar("_BACKEND_SERVICE") + "/roundtrip"
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
    destination_api = getEnvVar("_BACKEND_SERVICE") + "/failedflow"
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


@app.get("/unhandledexception")
def unhandledException():
    destination_api = getEnvVar("_DUMMY_SERVICE") + "/dummy"
    print("destination_api: ", destination_api)
    response = requests.get(destination_api, verify=False)
    return JSONResponse(status_code=response.status_code,
                        content={"response": response.json(), "ReturnCode": response.status_code})


@app.get("/custom/{httpcode}")
def customHttpCode(httpcode: int):
    return JSONResponse(status_code=httpcode,
                        content={"response": "Responding back with input HTTP response code", "ReturnCode": httpcode})


@app.get("/slowdb")
def slowDb():
    destination_api = getEnvVar("_BACKEND_SERVICE") + "/slowdb"
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
    destination_api = getEnvVar("_BACKEND_SERVICE") + "/sleep"
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


@app.get("/frontend/health")
def returnHealth():
    health_status = {"Status": "OK",
                     "uptime": jsonable_encoder(uptime()),
                     "boottime": jsonable_encoder(boottime())
                     }
    return JSONResponse(status_code=200, content=health_status)


@app.get("/backend/health")
def checkBackendServiceHealth():
    destination_api = getEnvVar("_BACKEND_SERVICE") + "/health"
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

    return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/dbservice/health")
def checkDbServiceHealth():
    destination_api = getEnvVar("_DB_SERVICE") + "/health"
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

    return JSONResponse(status_code=response.status_code, content=response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
