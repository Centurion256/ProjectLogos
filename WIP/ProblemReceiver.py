import requests
import json
import time

def GetProblem(subject, problem_type, difficulty):
    while True:
        try:
            raw_url = "https://math.ly/api/v1/"
            url = "{}{}/{}.json?difficulty={}".format(raw_url, subject, problem_type, difficulty)
            result = requests.get(url)
            time.sleep(2)
            return result.json()
        except:
            print("Resubmitting request...")
            time.sleep(4)
            continue

def Create_a_template(js):

    import json
    
    with open('template.json', 'w', encoding='utf-8') as f:

        json.dump(js, f, ensure_ascii=False, indent=4)

    return None

if __name__ == '__main__':

    Create_a_template(GetProblem('calculus', 'polynomial-integration', 'intermediate'))