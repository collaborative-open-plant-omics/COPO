import pymongo
from pymongo import ReturnDocument
import pymongo.errors as pymongo_errors
import urllib.parse
import re


username = urllib.parse.quote_plus("copo_user")
password = urllib.parse.quote_plus("password")
myclient = pymongo.MongoClient("mongodb://%s:%s@copo_mongo:27017/" % (username, password))
mydb = myclient["copo_mongo"]
regex = '([^(]+[$)])'

profile_collection = mydb['Profiles']
cursor = profile_collection.find({})

for profile in cursor:
    if "associated_type" in profile:
        if profile["associated_type"] == "":
            print("profile:" + profile["title"], " empty associated type")
            result = profile_collection.update_one({"_id": profile["_id"]}, {"$set": {"associated_type": []}})
            print(result.matched_count)
        else:
            associated_type = profile["associated_type"]
            final_associated_type = []

            for i in associated_type:
                if isinstance(i, str):
                    acronym = re.search(regex, i).group(1) if re.search(regex, i) else i
                    # Replace underscores with dashes
                    #acronym = acronym.replace("_", "-")
                    acronym = acronym.replace(")", "")
                    #i = i.replace("_", "-")
                    final_associated_type.append({'value': acronym, 'label': i})
                print("Profile:", profile["title"])
                print("Original:", associated_type)
                print("New:", final_associated_type)
                
            if final_associated_type:
                result = profile_collection.update_one({"_id": profile["_id"]},
                                                       {"$set": {"associated_type": final_associated_type}})
                print(result.matched_count)
    else:
        print("Profile:" + profile["title"], " no associated type")
        result = profile_collection.update_one({"_id": profile["_id"]},
			                           {"$set": {"associated_type": []}})
        print(result.matched_count)
