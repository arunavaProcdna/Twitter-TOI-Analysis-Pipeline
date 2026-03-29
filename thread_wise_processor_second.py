import pandas as pd

import json,time
from llm_call import get_relevance_score

llm_counter = 0
def call_llm(text):
    global llm_counter
    llm_counter += 1
    # return get_relevance_score({"text":text})
    return ["text"]


def check_cahe_else_llm(toi, tweet_id, text):
    if tweet_id:
        if toi.get(tweet_id):
            return toi.get(tweet_id)
        else:
            return call_llm(text)


def deduplicate_buckets(value):

    if not isinstance(value, list):
        return value

    toi_set = set()

    for item in value:
        if isinstance(item, str):

            # split comma separated TOIs
            parts = [x.strip() for x in item.split(",")]

            for p in parts:
                if p:
                    toi_set.add(p)

    # keep consistent order
    final_list = sorted(toi_set)

    return [", ".join(final_list)]




def process_each_mapping(INPUT_FILE):
        
    with open(INPUT_FILE, "r") as f:
        threads = json.load(f)
    toi = {}


    all_result=[]
    for thread in threads:

        for tweet in thread:

           

            
            referenced_tweets_type = tweet.get("referenced_tweets_type")
            text=tweet.get("text")
            tweet_id = tweet.get("tweet_id")
            referenced_tweets_id = tweet.get("referenced_tweets_id")
            block_no=tweet.get("block_no")
            
            # means this is parent
            
            if referenced_tweets_id == "None":

                

                response = check_cahe_else_llm(toi, tweet_id, text)

                toi[tweet_id] = response


            elif referenced_tweets_type == "quoted" or referenced_tweets_type == "replied_to":

            

                parts = text.split("@@")

                
                commentrytext = parts[0]
                original_text = parts[1]

                commentry_toi = call_llm(commentrytext)
                origignal_toi = check_cahe_else_llm(toi, referenced_tweets_id, original_text)

                
                merged = list(set(origignal_toi + commentry_toi))
                toi[tweet_id] = merged
            else:

            

                response = check_cahe_else_llm(toi, referenced_tweets_id, text)

                toi[tweet_id] = response








            result = {
                "tweet_id": tweet_id,
                "referenced_tweets_id":referenced_tweets_id,
                "referenced_tweets_type":referenced_tweets_type,
                "text":text,
                "Relevance": toi[tweet_id],
                "group":block_no
                
            }

            all_result.append(result)


            
    return all_result


def toiExtraction(INPUT_FILE, OUTPUT_FILE):

    results = process_each_mapping(INPUT_FILE)

    # Convert to list ONLY if you need full dataset
    

    df = pd.DataFrame(results)

    df["Relevance"] = df["Relevance"].apply(deduplicate_buckets)
     
    with open(OUTPUT_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4)


    excel_file = OUTPUT_FILE.replace(".json", ".xlsx")
    df.to_excel(excel_file, index=False)

    print(f"JSON saved: {OUTPUT_FILE}")
    print(f"Excel saved: {excel_file}")
    print(f"Results saved to {len(results)}")
    print("Total LLM Calls:", llm_counter)
    return df