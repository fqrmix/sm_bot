# Shopmaster Telegram Bot
## Description
Это бот, который...

## Using
1. Clone the repo:
```
git clone https://github.com/fqrmix/sm_bot.git
```

2. Instal the requirements:
```
pip install -r requirements.txt
```

3. Run main.py:
```
pyhton main.py
```

## Bot commands

- > **/load** - Load a shedule for next month;
- > **/today** - Get a today shift workers;
- > **/lunch** - Send a lunch-poll;
- > **/out** - Go out for lunch.


## Project architecture
```
- /sm_bot - [#] Root folder
  - /csv/
    - employers-next.csv - [#] Employer's schedule for next month
    - employers.csv - [#] Employer's schedule for current month
    - employers_5_2.csv - [#] Employer's schedule for 5/2
  - /json/
    - employers_info.json - [#] List of employers and info
    - employers_month.json - [#] List of month names on Russian language
    - employers_shift.json - [#] Work shift parameters
  - config.py - [#] Configuration file
  - main.py - [#] Main file
  - requirements.txt - [#] Requirements for using
  - telegram-bot.log [#] Logger
```

## CSV architecture
> If work_shift is empty - employers doesn't work today
```
Month;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30;31
Employer name[1];;;4;;;4;4;;4;4;;;4;;2;2;;;2;2;;;;;;4;4;;;4;4
Employer name[2];1;3;;;1;1;;1;;1;1;;1;4;;;1;1;;1;1;;;;;1;1;;1;;
.........
Employer name[n] work_shift;work_shift;work_shift;work_shift;work_shift;work_shift;....work_shift
```

## Working shift's
> JSON file with following format (all parameters are Str()):
```
{
    "1": {
        "start" : "08:00",
        "end" : "20:00"
    },
    "2": {
        "start" : "20:00",
        "end" : "08:00"
    },
    "3": {
        "start" : "10:00",
        "end" : "19:00"
    },
    "4": {
        "start" : "12:00",
        "end" : "00:00"
    },
    "5": {
        "start" : "00:00",
        "end" : "12:00"
    },
    "6": {
        "start" : "09:00",
        "end" : "18:00"
    }
}
```

## Employers info
> JSON file with following format (all parameters are Str()):
```
{
    "Employer_name_1" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)"
    },
    "Employer_name_2" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)"
    },
    .........
    "Employer_name_n" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)"
    }
}
```
