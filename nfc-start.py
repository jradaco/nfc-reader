import time
import requests
import math
import random
from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *

TOKEN = "..."  # Put your TOKEN here
DEVICE_LABEL = "nfc-reader"  # Put your device label here 
VARIABLE_LABEL_1 = "nfc"  # Put your first variable label here

MY_DATABASE = {
    "4b010100440807049f7bcac33e80": "Diana Marcela Rodriguez",
    "4b01010004080494d40c03": "Juan Sebastian Rada"
   }

def database(nfc_value):
    if nfc_value in MY_DATABASE:
        return MY_DATABASE[nfc_value]
    else:
        random_user_id = random.randint(0,999)
        return "New User " + str(random_user_id)
    
def poll_reader():
    pn532 = Pn532_i2c()
    pn532.SAMconfigure()
    card_data = pn532.read_mifare().get_data()   
    return card_data.hex()

def build_payload(variable_1):
    # Creates two random values for sending data
    value_1 = poll_reader()
    value_2 = database(value_1)
    print("[INFO] card data: " + value_1)
    print("[INFO] card data: " + value_2)   
    # Creates Payload
    payload = {variable_1: {"value": 1, "context": {"uuid": value_1, "username": value_2}}}

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    while (True):
        main()
        time.sleep(1)
