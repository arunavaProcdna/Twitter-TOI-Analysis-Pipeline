# import json
# from collections import Counter

# # ---- 1. Load data ----
# with open("recent_mapping_flow.json", "r") as f:
#     data = json.load(f)

# # ---- 2. Normalize function (remove consecutive duplicates) ----
# def normalize(flow):
#     normalized = []
#     for f in flow:
#         if not normalized or normalized[-1] != f:
#             normalized.append(f)
#     return tuple(normalized)

# # ---- 3. Extract flows ----
# flows = []
# normalized_flows = []

# for block in data:
#     # extract sequence of tweet types
#     flow = [node["referenced_tweets_type"] for node in block]
    
#     flows.append(tuple(flow))
#     normalized_flows.append(normalize(flow))

# # ---- 4. Count unique flows ----
# flow_counts = Counter(normalized_flows)

# # ---- 5. Print results ----
# print("\n🔹 Unique Flow Types and Counts:\n")

# for flow, count in flow_counts.items():
#     print(f"{flow}  -->  {count}")

# print("\nTotal unique flow types:", len(flow_counts))




import json
from collections import Counter, defaultdict

# ---- Load data ----
with open("recent_mapping_flow.json", "r") as f:
    data = json.load(f)

# ---- Normalize function ----
def normalize(flow):
    normalized = []
    for f in flow:
        if not normalized or normalized[-1] != f:
            normalized.append(f)
    return tuple(normalized)

# ---- Extract flows ----
flow_to_blocks = defaultdict(list)
normalized_flows = []

for block in data:
    flow = [node["referenced_tweets_type"] for node in block]
    norm_flow = normalize(flow)
    
    normalized_flows.append(norm_flow)
    flow_to_blocks[norm_flow].append(block)

# ---- Count flows ----
flow_counts = Counter(normalized_flows)

# ---- Prepare results ----
results = []

for flow, count in flow_counts.items():
    flow_str = f"{flow} --> {count}"
    
    sample_block = flow_to_blocks[flow][0]

    results.append({
        "flow_type": flow_str,
        "flow_tuple": list(flow),   # JSON-friendly version
        "count": count,
        "sample_block": sample_block
    })

# ---- Save to JSON ----
with open("flow_analysis.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Saved to /mnt/data/flow_analysis.json")