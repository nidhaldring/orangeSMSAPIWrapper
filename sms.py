import requests
from  urllib.request  import quote


class SmsSender:

    def __init__(self,authHeader:str,simNumber:str,countryCode:str="216"):
        self.authHeader = authHeader
        self.simNumber = simNumber
        self.countryCode

    def getToken(self) -> str:
        r = requests.post(
            url = "https://api.orange.com/oauth/v2/token",
            headers = {"Authorization" : self.authHeader },
            data = {"grant_type" : "client_credentials"}
        )
        
        return  dict(r.json().items()).get("access_token")


    def hasBalance(self) -> bool:

        r = requests.get(
            url = "https://api.orange.com/sms/admin/v1/contracts",
            headers = {"Authorization" : "Bearer " + self.getToken()}
        )

        data = dict(r.json().items())

        try:
            contracts =  data.get("partnerContracts").get("contracts")[0]
            serviceContracts = contracts.get("serviceContracts")[0]
            units = serviceContracts.get("availableUnits")
        except:
            # in case of errors return false
            return False    

        return units > 0
                

    def sendSms(self,receiverNumber:str,msg:str) -> None:
        if not self.hasBalance():
            print("you have zero balance,please recharge !")
            return

        url = f"https://api.orange.com/smsmessaging/v1/outbound/{quote(f'tel:+{self.simNumber}')}/requests"
        r = requests.post(
            url = url,
            headers = {
                "Authorization" : "Bearer "+self.getToken(),
                "Content-Type" : "application/json",
            },
            json = {
                    "outboundSMSMessageRequest": {
                    "address": f"tel:+{self.countryCode + receiverNumber}",
                    "outboundSMSTextMessage": { 
                            "message": f"{msg}"
                    },
                    "senderAddress": f"tel:+{self.simNumber}",
                }
            }
        )
        