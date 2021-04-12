import markov
from typing import Optional
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read_item(length: Optional[str] = None, start: Optional[str] = None):
    if length is not None:
        length = int(length)

    text = markov.generate(length=length, start=start)
    return text
