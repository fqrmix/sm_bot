FROM python:3.9 as builder

WORKDIR /usr/src/

COPY ./requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir ./wheels -r ./requirements.txt


FROM python:3.9-slim

WORKDIR /usr/src/
COPY --from=builder /usr/src/wheels ./wheels

RUN pip install --no-cache ./wheels/* && rm -rf ./wheels && pip install typing-extensions --upgrade
# # RUN mkdir ./sm_bot

# # COPY . ./sm_bot
# RUN mkdir ./logs

CMD bash ./sm_bot/runner.bash