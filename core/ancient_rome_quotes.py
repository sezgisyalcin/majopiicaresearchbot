
import json, random, os

BASE_DIR=os.path.dirname(os.path.dirname(__file__))

def load(author):
    path=os.path.join(BASE_DIR,"data",f"ancient_rome_quotes_{author}.json")
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)["items"]

def pick(author=None):
    authors=["cicero","caesar","seneca","marcus","augustus"]
    items=[]
    if author and author in authors:
        items=load(author)
    else:
        for a in authors:
            items+=load(a)
    if not items:
        raise ValueError("Dataset empty")
    return random.choice(items)
