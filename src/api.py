from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from webdavmediator import WebDavMediator
from pydantic import BaseModel, validator
from typing import Annotated
from collections import defaultdict
from time import strptime
from io import BytesIO
import pandas as pd

import uvicorn
import secrets
import os
import json
from dotenv import load_dotenv
from sm_bot.services.logger import logger

load_dotenv()

app = FastAPI()
security = HTTPBasic()

USER_DATA_PATH = './sm_bot/src/sm_bot/data'

def get_current_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(os.environ.get('API_LOGIN'), "utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(os.environ.get('API_PASSWORD'), "utf8")
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
    telegram_id: str
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
        if key not in ["ShopMaster", "Poisk", "LK", "CMS", "CMS & LK"]:
            raise ItemValidationException('ItemValidationException - group must be: "ShopMaster", "Poisk", "LK", "CMS" or "CMS & LK"')
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

    if (user.generate_webdav):
        logger.info(msg=f"[smbot-api] Users generate_webdav was true. Trying to generate webdav data")
        try:
            webdav_mediator = WebDavMediator(user)
            webdav_mediator.push_user_to_webdav_server()
            user_webdav_password = webdav_mediator.userdata.password
        except Exception as e:
            logger.error(msg=f"[smbot-api] Exception was caused by WebDavMediator: " + e)
    else:
        user_webdav_password = None


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
                "url": f"https://webdav.fqrmix.ru/{user.telegram}/1db301ea-2157-11ed-b5e3-a4423b714ddb/",
                "password": user_webdav_password
            }
        }
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)
        logger.info(msg=f"[smbot-api] User was successfully added. New user info: {json_data[user.username]}")

    return user

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


if __name__ == "__main__":
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=7772, 
        reload=False, 
        log_level="debug",
        root_path='/smbot/api/v1',
        workers=1
    )
