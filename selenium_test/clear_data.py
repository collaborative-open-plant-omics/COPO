import pymongo
from pymongo import ReturnDocument
import pymongo.errors as pymongo_errors
import urllib.parse

username = urllib.parse.quote_plus("copo_user")
password = urllib.parse.quote_plus("password")
myclient = pymongo.MongoClient("mongodb://%s:%s@copo_mongo:27017/" % (username, password))
mydb = myclient["copo_mongo"]

def drop_collection(name):
    print(f"Drop {name}")
    mycol = mydb[name]
    mycol.drop()
    print(f"{name} dropped")

drop_collection("SampleCollection")
drop_collection("SourceCollection")
drop_collection("SubmissionCollection")
drop_collection("ValidationQueueCollection")
drop_collection("Profiles")
drop_collection("DataFileCollection")
drop_collection("EnaFileTransferCollection")
drop_collection("AssemblyCollection")
drop_collection("SeqAnnotationCollection")
drop_collection("SubmissionQueueCollection")
