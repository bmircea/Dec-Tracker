import os
import json

with open("config.json", "r+") as f:
    config = json.load(f)
    f.close()


LOGGER.setLevel(logging.WARNING)
path = config["PATHS"]["main"]
dec_path = os.path.join(path, "dec")
pdf_path = os.path.join(path, "recipise")
chromedriver_exe = config["PATHS"]["chromedriver"]
xml_path = os.path.join(path, "DecUnica.xml")
headless = config["PATHS"]["headless"]
