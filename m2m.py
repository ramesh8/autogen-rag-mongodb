import random
import mysql.connector
from pymongo import MongoClient
import math

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="setu"
)

mongo = MongoClient("mongodb+srv://root:620750648@demo.zzg5m.mongodb.net/")
mdb = mongo["SME"]
mcol = mdb["questions"]

td = mcol.find_one({})
print(td)

mycursor = mydb.cursor()

def get_options(qid):
    mycursor.execute(f"SELECT option FROM question_options AS qo WHERE qo.question_id='{qid}'")
    res = mycursor.fetchall()
    return res

# def get_mongo(qid):
#     res = mcol.find_one({"question_id":qid},{"_id":0})
#     return res

def update_mongo(q):
    res = mcol.update_one({"question_id":q["question_id"]},{"$set":q}, upsert=False)
    return res.raw_result

def insert_mongo(q):
    res = mcol.insert_one(q)
    return res


# getting largest questions first
mycursor.execute("SELECT question_id, question, answer FROM question_info ORDER BY CHAR_LENGTH(question) DESC LIMIT 1, 1000")

myresult = mycursor.fetchall()

for (qid, qtxt, qans) in myresult:
    qops = get_options(qid)
    ops = [str(o[0]) for o in qops]
    sid = random.choice([1,2,3,4,5])
    dl = random.randint(1,5)
    q = {
            "question_id":      qid,
            "skill_id" : sid,
            "question_text":    str(qtxt),
            "question_type":    "MCQ",
            "difficulty_level": dl,
            "options":          ops,
            "correct_answer":   qans 
        }
    # print(q)
    
    # q["question_text"] = qtxt
    # q["question_type"] = "MCQ"
    # q["options"] = qops
    # q["correct_answer"] = qans
    # print(q)

    print(insert_mongo(q))