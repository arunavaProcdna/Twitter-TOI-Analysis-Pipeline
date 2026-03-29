


import json
import pandas as pd

def SavefinalOutput(EXTRACTED_DATAFRAME,MAIN_INPUT_FILE,FINAL_OUTPUT_FILE):
   
    # EXTRACTED_DATAFRAME = pd.read_excel("analysis/raw_output/toi_results.xlsx")
    main_df = pd.read_excel(MAIN_INPUT_FILE)
    EXTRACTED_DATAFRAME = EXTRACTED_DATAFRAME[["tweet_id", "Relevance"]]
    final_df = EXTRACTED_DATAFRAME.merge(main_df, on="tweet_id", how="left")
    final_df.to_excel(FINAL_OUTPUT_FILE, index=False)

    print(f"Filtered file saved: {FINAL_OUTPUT_FILE}")
    print(f"Matching rows: {len(final_df)}")




def convert_json_toexcel(MAP_INPUT_FILE,MAP_OUTPUT_FILE):
    with open(MAP_INPUT_FILE) as f:
        data = json.load(f)

    rows = []

    for block_no, block in enumerate(data, start=1):   # auto block numbering
        for level, item in enumerate(block, start=1):  # level inside block
            
            rows.append({
                "block_no": block_no,
                "level": level,
                "type": item.get("referenced_tweets_type"),
                "tweet_id": (item.get("tweet_id")),
                "referenced_tweet_id": (item.get("referenced_tweets_id")),
                "text":item.get("text")
                
            
            })

    df = pd.DataFrame(rows)

    df.to_excel(MAP_OUTPUT_FILE, index=False)
   