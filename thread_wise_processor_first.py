import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from utlity_graph import topological_sort_threadwise,visualization
from collections import deque
import json



def convert_and_df(df):
    df["tweet_id_str"] = df["tweet_id"]
    df["referenced_tweets_id_str"] = df["referenced_tweets_id"]
    return df




def thread_wise_process(INPUT_FILE,OUTPUT_FILE):
        
    
    df = pd.read_excel(INPUT_FILE, sheet_name="orginal")
    # # df  = df.iloc[2456:2461]
    # df  = df.iloc[1973:1974]
    print(df[["tweet_id", "referenced_tweets_id", "referenced_tweets_type"]])
    # Convert tweet_id to string

    df=convert_and_df(df)
   
    # processed df
    # df = pd.DataFrame(data)
    # df=df.head(5)
    # visualization(df)

    edges = df[df['referenced_tweets_id'].notna()][['referenced_tweets_id','tweet_id']].values.tolist()



    toplist=topological_sort_threadwise(edges)


    tweet_info = df.set_index('tweet_id')[['referenced_tweets_type','referenced_tweets_id','tweet_id_str','referenced_tweets_id_str',"text"]].to_dict(orient='index')
    tweet_ids = set(df['tweet_id'])
    # ================== Prepare JSON-like output ==================
    output = []
    for thread in toplist:
        thread_list = []
        for tweet_id in thread:
            if tweet_id in tweet_info:
                ref_id = tweet_info[tweet_id]['referenced_tweets_id']
                if pd.isna(ref_id) or ref_id is None or ref_id not in tweet_ids:
                    ref_id_clean = "None"
                else:
                    ref_id_clean = ref_id
                thread_list.append({
                    # "ex_tweet_id":tweet_info[tweet_id]['tweet_id_str'],
                    # "ex_referenced_tweets_id":tweet_info[tweet_id]['referenced_tweets_id_str'],
                    "referenced_tweets_type": tweet_info[tweet_id]['referenced_tweets_type'],
                    "text":tweet_info[tweet_id]['text'],
                    "tweet_id": tweet_id,
                    "referenced_tweets_id": ref_id_clean,


                })
        output.append(thread_list)


    # ---- Add single tweets not present in threads ----
    thread_tweet_ids = {t["tweet_id"] for thread in output for t in thread}
    # print(df.head(5))
    for _, row in df.iterrows():
        if row["tweet_id"] not in thread_tweet_ids:
            output.append([{
                # "ex_tweet_id":tweet_info[tweet_id]['tweet_id_str'],
                # "ex_referenced_tweets_id":tweet_info[tweet_id]['referenced_tweets_id_str'],
                "referenced_tweets_type": row["referenced_tweets_type"],
                "text":row["text"],
                "tweet_id": row["tweet_id"],
                "referenced_tweets_id": "None"
            }])



    # Print JSON-like array
    for i, block in enumerate(output, start=1):
        for row in block:
            row["block_no"] = i

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)





