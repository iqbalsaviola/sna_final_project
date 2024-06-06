import json
import base64
import re
import os


def extract_profile(data) -> list:
    return data['data']['user']

def extract_followings(data) -> list:
    friendship_api_url = r'https://www.instagram.com/api/v1/friendships/.*/following'

    contents = [entry['response']['content'] for entry in data ['log']['entries']
                if re.match(friendship_api_url, entry['request']['url'])]
    
    # Extract JSON data

    users = []
    for content in contents:
        if 'text' not in content:
            continue
        text = content['text']

        if 'encoding' in content:
            encoding = content['encoding']
            if encoding == 'base64':
                decodedBytes = base64.b64decode(text)
                decodedStr = str(decodedBytes, 'utf-8')
                user_json = json.loads(decodedStr)
                users.extend(user_json['users'])
        else:
            user_json = json.loads(text)
            users.extend(user_json['users'])
    return users

def extract_person(person: str):
    with open(f'./data/{person}/following.har', 'r', errors='ignore') as f:
        data = json.loads(f.read())
        followings = extract_followings(data)
    
    with open(f'./data/{person}/profile.json', 'r') as f:
        data = json.loads(f.read())
        profile = extract_profile(data)
    
    output = {
        'general': profile,
        'followings': followings
    }
    return output, profile['id']
    

def extract_all():
    persons = os.listdir('./data')
    
    users = {}
    for person in persons:
        output, id = extract_person(person)
        users[id] = output

    with open('./out/people.json', 'w') as f:
        f.write(json.dumps(users))

extract_all()
