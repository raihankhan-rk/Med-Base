import requests
from util.pinata import *


class Ipfs:
    @staticmethod
    def pinToIpfs(path):
        headers = {
            "pinata_api_key": API_KEY,
            "pinata_secret_api_key": API_SECRET,
        }

        with open(path, 'rb') as file:
            files = {"file": file.read()}
            resp = requests.post(ENDPOINT, headers=headers, files=files)

        if resp.status_code == 200:
            # print(f"file upload successful")
            # print(f"{DWEB_GATEWAY}{resp.json()['IpfsHash']}")
            # print(resp.json())
            timestamp = resp.json()["Timestamp"]
            timestamp = timestamp.replace("T", "-")
            temp = timestamp.split("-")
            date = f"{temp[2]}-{temp[1]}-{temp[0]}"
            return resp.json(), date

    # pinToIpfs("/Users/raihankhan/PycharmProjects/MedBase/Backend/uploads/download_9.png")