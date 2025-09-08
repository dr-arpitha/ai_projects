from typing import Optional

from pydantic import BaseModel, ValidationError, EmailStr
import json
from pydantic import Field

class UserInput(BaseModel):
    name:str
    email:EmailStr
    query:str
    orderid: Optional[int] = Field(
        None,
        description="5-digit order number (cannot start with 0)",
        ge=10000,
        le=99999
    )
    purchaseDate: Optional[int] = None


def validate_user_query(inputData):
    try:
        userInput = UserInput(**inputData)
        print("Valid input model generated")
        print(f"{userInput.model_dump_json(indent=2)}")
    except ValidationError as e:
        print("Validation errors have occurred")
        for error in e.errors():
            print(f" - {error['loc']} : {error['msg']}")


def call_main_func():
    userInput = {
        "name":"TestAgent",
        "email":"testagent@gmail.com",
        "query":"How to get gemini API key"
    }
    validate_user_query(userInput)

    print("Using json objects")
    inputJson = '''{
        "name": "Joe User",
        "email": "joe.user@example.com",
        "query": "I bought a keyboard and mouse and was overcharged.",
        "order_id": 12345,
        "purchase_date": "2025-12-31"
    }'''
    inputData = json.loads(inputJson)
    validate_user_query(inputData)

    print("Using invalid json objects")
    json_invalid_data = '''
    {
        "name": "123",
        "email": "joe.user@example.com",
        "query": "My account has been locked for some reason.",
        "order_id": "1",
        "purchase_date": "295-12-31"
    }
    '''
    try :
        user_invalidate_error = UserInput.model_validate_json(json_invalid_data)
        print(user_invalidate_error.model_dump_json(indent=2))
    except ValueError as ve:
        print(ve.errors())
        # print(user_invalidate_error.model_dump_json(indent=2))

if __name__ == "__main__":
    call_main_func()