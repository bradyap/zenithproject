import json

filename = "../content/gif_links.json"

with open (filename) as f:
    data = json.load(f)
print("Enter gif category: ")
cat = str(input())
print("Enter gif links:")

user_input = str(input())

while user_input != "exit":
    split = user_input.split("?", 1)
    link = split[0]
    print("Parsed: " + link)
    data[cat].append(link)
    with open (filename, 'w') as f:
        json.dump(data, f, indent=4)
    print("Saved.")
    user_input = str(input())