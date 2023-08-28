import requests

headers = {
    'X-Auth-Token': '7XNPnjgDRfZdZbbkvhb5j0HeeWkqX0eEPOUrhIXNZ5a',
    'X-User-Id': 'mKDHoxweEKeAxNu4D',
    'Content-type': 'application/json',
}

json_data = {
    'daysIdle': 35,
    'role': 'admin',
}

response = requests.post('http://chat.grandoffice.by:80/api/v1/users.deactivateIdle', headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{ "daysIdle": 2, "role": "admin" }'
#response = requests.post('http://chat.grandoffice.by:3000/api/v1/users.deactivateIdle', headers=headers, data=data)

print(response.json())