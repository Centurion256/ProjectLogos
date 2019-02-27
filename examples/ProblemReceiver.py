from pprint import pprint
import requests
raw_url = "https://math.ly/api/v1/"
subject = "algebra/"
problem_type = "linear-equations"
difficulty = "beginner"
url = raw_url + subject + problem_type + ".json?difficulty=" + difficulty
result = requests.get(url)
r = result.json()
pprint(r)