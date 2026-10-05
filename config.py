import os

from dotenv import load_dotenv

load_dotenv()

INTERVALS_ICU_API_KEY = os.environ["INTERVALS_ICU_API_KEY"]
INTERVALS_ICU_ATHLETE_ID = os.environ["INTERVALS_ICU_ATHLETE_ID"]

PENDELSTRECKE_KM = float(os.environ.get("PENDELSTRECKE_KM", "36"))
TRAININGSEINHEITEN_PRO_WOCHE = int(os.environ.get("TRAININGSEINHEITEN_PRO_WOCHE", "2"))
FTP_STARTWERT = int(os.environ.get("FTP_STARTWERT", "280"))
TRAININGSMETHODIK = os.environ.get("TRAININGSMETHODIK", "sweet_spot")
TRAININGSZIEL = os.environ.get("TRAININGSZIEL", "")
