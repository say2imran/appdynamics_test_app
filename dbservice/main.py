from typing import Optional
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
import requests
import time
import uvicorn
from uptime import uptime, boottime
import sqlite3

app = FastAPI()

defaultEnv = {
    "_BACKEND_SERVICE": "http://" + "backend-service",
    "_FRONTEND_SERVICE": "http://" + "frontend-service",
    "_DB_SERVICE": "http://" + "db-service",
    "_DEFAULT_SLEEP": 1,
    "_INCREMENTAL_SLEEP": 3
}


def getEnvVar(envVar):
    if envVar not in os.environ:
        return defaultEnv[envVar]
    else:
        return os.environ[envVar]


def returnDbConnection():
    conn = sqlite3.connect('testDB.db')
    return conn


@app.get("/")
def baseUrl():
    return {"Microservice": "DB Service"}


@app.get("/roundtrip")
def roundTrip():
    return JSONResponse(status_code=200,
                        content={"response": "Returning 200 from DB Service", "ReturnCode": 200})


@app.get("/dbquery")
def slowDb():
    slow_query = """select """
    start_time = time.time()
    cursor = returnDbConnection().cursor()
    cursor.execute(slow_query)
    output = cursor.fetchall()
    time_taken = time.time() - start_time
    print("Time taken by query: {}".format(time_taken))
    return JSONResponse(status_code=200,
                        content={"time_taken": time_taken, "ReturnCode": 200})


@app.get("/slowdbquery")
def slowDb():
    slow_query = """WITH RECURSIVE r(i) AS (VALUES(0) 
    UNION ALL
    SELECT i FROM r
    LIMIT 1000000
    ) SELECT i FROM r WHERE i = 1;"""
    start_time = time.time()
    cursor = returnDbConnection().cursor()
    cursor.execute(slow_query)
    output = cursor.fetchall()
    time_taken = time.time() - start_time
    print("Time taken by query: {}".format(time_taken))
    return JSONResponse(status_code=200,
                        content={"time_taken": time_taken, "ReturnCode": 200})


@app.get("/sleep/{seconds}")
def sleep(seconds: int):
    if not 0 <= seconds <= 10:
        seconds = defaultEnv["_DEFAULT_SLEEP"]

    sleep_seconds = seconds + getEnvVar("_INCREMENTAL_SLEEP")
    print("Sleeping for : {} seconds".format(sleep_seconds))
    time.sleep(sleep_seconds)

    return JSONResponse(status_code=200,
                        content={"response": "Responding back from DB Service after sleep: {} seconds".format(sleep_seconds),
                                 "ReturnCode": 200})


@app.get("/health")
def returnHealth():
    health_status = {"Status": "OK",
                     "uptime": jsonable_encoder(uptime()),
                     "boottime": jsonable_encoder(boottime())
                     }
    return JSONResponse(status_code=200, content=health_status)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
