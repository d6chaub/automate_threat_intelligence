import datetime
import logging
import os
import sys

import azure.functions as func
from ingestion_pipeline import run_ingestion_pipeline

app = func.FunctionApp()

@app.function_name(name="alerts_ingestion_cronjob_func")
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="ingestiontimer", run_on_startup=True, use_monitor=False) 
def timer_trigger_ingestion_pipeline(ingestiontimer: func.TimerRequest) -> None:
    if ingestiontimer.past_due:
        logging.info('The ingestiontimer is past due!')

    init_utc_timestamp = datetime.datetime.now(datetime.timezone.utc)

    logging.info('Ingestion pipeline trigger function ran at %s', init_utc_timestamp.isoformat())

    logging.info("The pwd is: %s", os.getcwd())


    run_ingestion_pipeline()

    terminate_utc_timestamp = datetime.datetime.now(datetime.timezone.utc)

    logging.info('Ingestion pipeline trigger function completed at %s', terminate_utc_timestamp.isoformat())
    logging.info('Ingestion pipeline trigger function ran for %s', terminate_utc_timestamp - init_utc_timestamp)
    return