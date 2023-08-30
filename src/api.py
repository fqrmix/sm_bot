import secrets
from collections import defaultdict
from typing import Annotated, Union, Literal
from pydantic import BaseModel, validator
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from time import strptime

app = FastAPI()

security = HTTPBasic()


def get_current_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"login"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"password"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app = FastAPI(description="Shopmaster Bot API")

class ItemValidationException(Exception): ...

class UserItem(BaseModel):
    username: str
    telegram: str
    telegram_id: int
    group: str
    subscription_state: bool
    subscription_time: str
    generate_webdav: bool

    @validator('subscription_time')
    def validate_sub_time(cls, key, values):
        if (not values['subscription_state']):
            raise ItemValidationException('ItemValidationException - subscription_state is not true, but trying to set subscription_time')
        try:
            strptime(key, '%H:%M')
            return key
        except ValueError as e:
            raise ItemValidationException(e)

        
    @validator('group')
    def validate_group(cls, key, values):
        if key not in ["ShopMaster", "Poisk", "LK", "CMS"]:
            raise ItemValidationException('ItemValidationException - group must be: "ShopMaster", "Poisk", "LK" or "CMS"')
        return key


class BaseResponseModel(BaseModel):
    status: int
    body: dict
    error: str

@app.exception_handler(Exception)
async def custom_form_validation_error(request, exc):
    print(vars(exc))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"status": status.HTTP_400_BAD_REQUEST, "detail": "Invalid request", "errors": str(exc)}
        ),
    )

@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(request, exc):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"status": status.HTTP_400_BAD_REQUEST, "detail": "Invalid request", "errors": reformatted_message}
        ),
    )

@app.put("/users/")
def update_user(user: UserItem):
    return user

@app.post("/users/shifttype")
def change_shift_type(username: Annotated[str, Depends(get_current_credentials)], body: dict):
    return True

@app.post("/users/")
def add_user(username: Annotated[str, Depends(get_current_credentials)], body: dict):
    return True

@app.delete("/users/")
def delete_user(username: Annotated[str, Depends(get_current_credentials)], body: dict):
    return True


@app.put("/shift/fulltime/")
def update_fulltime_employee(username: Annotated[str, Depends(get_current_credentials)], body: dict):
    return True

@app.put("/shift/csv/")
def update_current_shifts(username: Annotated[str, Depends(get_current_credentials)], body: dict):
    return True

