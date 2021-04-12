import markov
from typing import Optional
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read_item(length: Optional[str] = None, start: Optional[str] = None):
    mark = markov.MakeMarkov()
    if length is not None:
        length = int(length)

    text = mark.generate(length=length, start=start)
    return text
