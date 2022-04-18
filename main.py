import uvicorn
import schedule
from scheduling.jobs import regression_analysis, regression_analysis_fake
from scheduling.constants import REALTIME_CHECK_PERIOD
import time


if __name__ == "__main__":
    schedule.every(REALTIME_CHECK_PERIOD).seconds.do(regression_analysis_fake)
    while True:
        uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
        schedule.run_pending()
        time.sleep(1)
