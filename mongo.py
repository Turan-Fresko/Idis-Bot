import pymongo
import dotenv
__mongo_token = dotenv.get_key(".env",key_to_get="MONGO")

client = pymongo.MongoClient(__mongo_token)

def get_client():
    return client