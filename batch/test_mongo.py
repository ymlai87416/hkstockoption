# to mimic the report stuff
import summary_config
import urllib
from datetime import datetime
from pymongo import MongoClient

def add_report(data):
    mongodbUrl = "mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".\
    format(urllib.parse.quote_plus(summary_config.mongo_user), 
        urllib.parse.quote_plus(summary_config.mongo_password), 
        summary_config.mongo_host)
    client = MongoClient(mongodbUrl)

    db = client[summary_config.mongo_db_name]
    #date_str = batchDate.strftime('%Y%m%d')
    collection = db["reports"]
    print(collection)
    print("hi2")
    db.reports.delete_many({"batch_date": data["batch_date"]})
    print("hi")
    result=collection.insert_one(data)
    client.close()


def main():
    result = dict()
    result["batch_date"] = datetime(2022, 7, 22)
    result["creation_time"] = datetime.now()
    result["title_text"] = "Test 1"
    add_report(result)

    result["creation_time"] = datetime.now()
    result["title_text"] = "Test 2"
    add_report(result)

if __name__=="__main__":
    main()