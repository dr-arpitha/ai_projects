from enum import Enum
from fastapi import FastAPI


class CompanyNameOption(str, Enum):
    synergy = "Synergy"
    cognic = "Congniq"
    a3 = "A3Solutions"

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.get("/model/{name}")
def company_name_options(name : CompanyNameOption) :
    if name == CompanyNameOption.synergy:
        value = f"Company name provided {name}"
        print(value)
        return value
    elif name.value == "Congniq":
        value = f"Company name provided {name}. It is cogniq right?"
        print(value)
        return value

    return 'f\"Going with default {name}.\"'

