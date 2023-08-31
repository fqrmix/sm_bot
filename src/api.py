from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator
from typing import Annotated
from collections import defaultdict
from time import strptime
from io import BytesIO
import pandas as pd
import secrets
import json


from sm_bot.services.logger import logger

app = FastAPI()
security = HTTPBasic()

USER_DATA_PATH = './sm_bot/data'

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
        if (values['subscription_state']):
            try:
                strptime(key, '%H:%M')
            except ValueError as e:
                raise ItemValidationException(e)
        return key

        
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

@app.get("/users/")
def get_users(username: Annotated[str, Depends(get_current_credentials)]):
    with open(USER_DATA_PATH + '/json/employers_info.json', "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    return json_data

@app.get("/users/{user_name}")
def get_users(username: Annotated[str, Depends(get_current_credentials)], user_name: str):
    with open(USER_DATA_PATH + '/json/employers_info.json', "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    try:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {"username": user_name, "user_info": json_data[user_name]}
            )
        )
            
    except KeyError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {"status": status.HTTP_400_BAD_REQUEST, "detail": "Invalid request", "errors": f"User {user_name} doesn't exist!"}
            )
        )

@app.put("/users/update")
def update_user(username: Annotated[str, Depends(get_current_credentials)], user: UserItem):
    with open(USER_DATA_PATH + '/json/employers_info.json', "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    try:
        previous_user_info = json_data[user.username]

    except KeyError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {"status": status.HTTP_400_BAD_REQUEST, "detail": "Invalid request", "errors": f"User {user.username} doesn't exist!"}
            )
        )
    
    with open(USER_DATA_PATH + '/json/employers_info.json', "w", encoding='utf-8') as json_file:
            json_data[user.username]['telegram'] = user.telegram
            json_data[user.username]['telegram_id'] = user.telegram_id
            json_data[user.username]['group'] = user.group
            json_data[user.username]['subscription']['enabled'] = user.subscription_state
            json_data[user.username]['subscription']['time_to_notify'] = user.subscription_time

            logger.info(msg=f"[smbot-api] User info was successfully updated. Updated user info: {json_data[user.username]}")

            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder(
                        {"msg": "User info was successfully updated", "updated_user_info": json_data[user.username]}
                    )
                )
@app.post("/users/add")
def add_user(username: Annotated[str, Depends(get_current_credentials)], user: UserItem):
    with open(USER_DATA_PATH + '/json/employers_info.json', "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    with open(USER_DATA_PATH + '/json/employers_info.json', "w", encoding='utf-8') as json_file:
        json_data[user.username] = {
            'telegram': user.telegram,
            'telegram_id': user.telegram_id,
            'group': user.group,
            'subscription': {
                'enabled': user.subscription_state,
                'time_to_notify': user.subscription_time
            },
            "webdav": {
                "name": "Work",
                "url": "https://www.www.www/",
                "password": "None"
            }
        }
        logger.info(msg=f"[smbot-api] User was successfully added. New user info: {json_data[user.username]}")
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)

    return user

# @app.post("/users/changeshifttype")
# def change_shift_type(username: Annotated[str, Depends(get_current_credentials)], body: dict):
#     return True

@app.get("/csv/shifts/")
def get_current_shifts_csv(username: Annotated[str, Depends(get_current_credentials)]):
    return FileResponse(USER_DATA_PATH + '/csv/employers.csv')

def _upload_file(path: str, uploaded_file: UploadFile = File(...)):
    contents = uploaded_file.file.read()
    buffer = BytesIO(contents)
    df = pd.read_csv(buffer)
    buffer.close()
    uploaded_file.file.close()
    df.to_csv(path, index=False)
    return df.to_string(index=False)

@app.put("/csv/shifts/update")
def update_current_shifts_csv(username: Annotated[str, Depends(get_current_credentials)], uploaded_file: UploadFile = File(...)):
    new_csv = _upload_file(USER_DATA_PATH + '/csv/employers.csv' ,uploaded_file)
    logger.info(msg=f"[smbot-api] Shift CSV file was successfully updated. New CSV:\n{new_csv}")

@app.get("/csv/fulltime")
def get_current_fulltime_csv(username: Annotated[str, Depends(get_current_credentials)]):
    return FileResponse(USER_DATA_PATH + '/csv/employers_5_2.csv')

@app.put("/csv/fulltime/update")
def update_current_fulltime_csv(username: Annotated[str, Depends(get_current_credentials)], uploaded_file: UploadFile = File(...)):
    new_csv = _upload_file(USER_DATA_PATH + '/csv/employers_5_2.csv' ,uploaded_file)
    logger.info(msg=f"[smbot-api] Fulltime CSV file was successfully updated. New CSV:\n{new_csv}")
