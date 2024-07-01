import requests

url = "http://127.0.0.1:8000/user/refresh"

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ5ZWFqaW4iLCJleHAiOjE3MTk4OTkzMDV9.yGtX1GqeF6GQ4XFdoJyYrnXk8ldZzOPy6xdWx3oJw4s"
}

response = requests.post(url, headers=headers)
print(response.status_code)
print(response.json())
