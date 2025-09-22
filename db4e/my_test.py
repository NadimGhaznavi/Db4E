
from datetime import datetime, timedelta
from json import loads
from urllib.error import URLError
from urllib.request import Request, urlopen
from typing_extensions import Final



from db4e.Constants.DMongo import DMongo
from db4e.Constants.DMining import DMining

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MiningDb import MiningDb


TEXTUAL_ICBM: Final[tuple[float, float]] = (55.9533, -3.1883)

db = DbMgr()
mdb = MiningDb(db=db)

h_recs = mdb.get_chain_hashrates(DMining.MAIN_CHAIN)
#h_recs = mdb.get_xmrigs_remote()

h_data = {}


def get_weather_data():
    end_date = (
        datetime.now() - timedelta(days=365) + timedelta(weeks=1)
    )  # Yes, yes, I know. It's just an example.
    start_date = end_date - timedelta(weeks=2)  # Two! Weeks!
    try:
        with urlopen(
            Request(
                "https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={TEXTUAL_ICBM[0]}&longitude={TEXTUAL_ICBM[1]}"
                f"&start_date={start_date.strftime('%Y-%m-%d')}"
                f"&end_date={end_date.strftime('%Y-%m-%d')}"
                "&hourly=temperature_2m,precipitation,surface_pressure,windspeed_10m"
            )
        ) as result:
            print(result.read().decode('utf-8'))
    except URLError as error:
        print(str(error))

