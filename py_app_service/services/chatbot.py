import py_app_service.config
from py_app_service.services.prompting import generate_completion
from py_app_service.database import mongo_instance
from pymongo import MongoClient


# SERVER PUBLIC MONGO DB
uri = py_app_service.config.MONGODB_URI
client_db = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client_db.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
client_db = client_db[py_app_service.config.MONGODB_NAME]
collection_business = client_db["business"]
collection_kbs = client_db["kbs"]

system_prompt_chatbot = """
You are a business consultant acting as user assistant. User wants to consult with you in bahasa (indonesian language) about his/her business.
You need to answer his/her question. If his/her question is related to the given context, than answer the question by referring the context.
Please response in bahasa (indonesian language).
"""
user_prompt_chatbot = """
### CONTEXT: <<context>>
### QUERY: <<query>>
### ANSWER:
"""

def update_kbs(business_id,payload_form):
    overview_builder = [i for i in collection_business.find({"business_id":business_id})][-1]["overview"]
    market_expansion_opportunities = [i for i in collection_business.find({"business_id":business_id})][-1]["market_opportunity"]
    gtm_strategy = [i for i in collection_business.find({"business_id":business_id})][-1]["gtm"]

    text_form= "====================== GENERAL INFORMATION ======================"
    for key,value in list(payload_form.items()):
        text_form += "\n"
        text_form += key + ": "+str(value)

    text_overview = "====================== OVERVIEW ======================"
    for key,value in list(overview_builder.items())[2:]:
        text_overview += "\n"
        text_overview += key + ": "+value

    text_market_expansion = "====================== MARKET EXPANSION OPPORTUNITIES ======================"
    market_expansion_text = market_expansion_opportunities
    key_replacements = {
        "strength_potential_chart":"strength_potential_chart (in a scale of 0-100)",
        "market_size_estimation_local": "market_size_estimation_local (in billion IDR)",
        "market_size_estimation_international":"market_size_estimation_international (in billion IDR)"
    }
    market_expansion_text = {key_replacements.get(k, k): v for k, v in market_expansion_text.items()}
    for key,value in list(market_expansion_text.items())[2:]:
        text_market_expansion += "\n"
        text_market_expansion += key + ": "+str(value)

    text_gtm = "====================== GO-TO-MARKET STRATEGY ======================"
    gtm_strategy_text = gtm_strategy
    key_replacements = {
        "milestone":"milestone focus dalam 5 tahun",
        "market_size_timeline":"market_size_timeline atau potensi_revenue dalam 5 tahun (in million IDR)"
    }
    gtm_strategy_text = {key_replacements.get(k, k): v for k, v in gtm_strategy_text.items()}
    for key,value in list(gtm_strategy_text.items())[2:]:
        text_gtm += "\n"
        text_gtm += key + ": "+str(value)


    combine_text = f"{text_form}\n\n{text_overview}\n\n{text_market_expansion}\n\n{text_gtm}"

    # output
    payload = {
        "business_id":business_id,
        "module":"knowledge_base",
        "content":combine_text
    }

    # sending to MongoDB
    collection_kbs.insert_one(payload)
    # return output
    return payload

def chatbot(business_id,query):
    kbs = [i for  i in collection_kbs.find({"business_id":business_id})][-1]["content"]
    response =  generate_completion(system_prompt_chatbot,user_prompt_chatbot.replace("<<query>>",query).replace("<<context>>",kbs))
    return response

