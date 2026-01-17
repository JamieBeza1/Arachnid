import json

json_data = {'vendor': 'n8n', 'product': 'n8n', 'version': 'unknown', 'confidence': 'high'}

def create_fingerprint(json_dict):
    print(json_dict["vendor"])


create_fingerprint(json_data)
