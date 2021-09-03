import json

filename = "../content/gif_links.json"

data = {}
data["hug"] = []
data["kiss"] = []
data["pat"] = []
data["punch"] = []
data["slap"] = []

with open (filename, 'w') as f:
    json.dump(data, f, indent=4)