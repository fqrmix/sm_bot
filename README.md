# Shopmaster Telegram Bot
## Description

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
- > **/workers** - Get a today shift workers;
```
Also it can be used that way:
[/workers +1] - Get list of tommorow workers
[/workers -1] - Get list of yesterday workers
[/workers 23] - Get workers which works at 23 day of current month
```
- > **/chatters** - Get a chatter list for today;
- > **/lunch** - Send a lunch-poll;
- > **/out** - Go out for lunch.
- > **/sub** - Subscription to notifications info
- > **/addchatter** - Add user to chat-list
- > **/removechatter** - Remove user from chat-list
- > **/webdav** - CalDAV sync settings


## Project architecture
```
|-- logs                                            [#] Log folder
|   `-- telegram-bot.log
|-- src
|   |-- sm_bot
|   |   |-- config                                  [#] Configuration module
|   |   |   `-- config.py
|   |   |-- data
|   |   |   |-- csv
|   |   |   |   |-- employers_5_2.csv               [#] Employer's schedule for next month
|   |   |   |   |-- employers.csv                   [#] Employer's schedule for current month
|   |   |   |   `-- employers-next.csv              [#] Employer's schedule for 5/2
|   |   |   `-- json
|   |   |       |-- employers_info.json             [#] List of employers and info
|   |   |       |-- employers_month.json            [#] List of month names on Russian language
|   |   |       `-- employers_shift.json            [#] Work shift parameters      
|   |   |-- handlers
|   |   |   |-- bot                                 
|   |   |   |   |-- callback                        [#] Bot callback handlers [#]
|   |   |   |   |   |-- chatters                        [##] Bot chatters callback handler
|   |   |   |   |   |   `-- chatters.py
|   |   |   |   |   |-- shifts                          
|   |   |   |   |   |   |-- addshift                    [##] Bot shift add callback handler
|   |   |   |   |   |   |   `-- addshift.py
|   |   |   |   |   |   |-- dayoff                      [##] Bot shift dayoff callback handler
|   |   |   |   |   |   |   `-- dayoff.py
|   |   |   |   |   |   `-- swapshift                   [##] Bot shift swap callback handler
|   |   |   |   |   |       `-- swapshift.py
|   |   |   |   |   `-- subscription
|   |   |   |   |       `-- subscription.py
|   |   |   |   `-- message                         [#] Bot message handlers [#]
|   |   |   |       |-- base                            [#][#] Basic commands
|   |   |   |       |   |-- botinit.py                      [#][#] /init command
|   |   |   |       |   |-- log.py                          [#][#] /log command
|   |   |   |       |   |-- lunch.py                        [#][#] /lunch command
|   |   |   |       |   `-- out.py                          [#][#] /out command
|   |   |   |       |-- chatters                        [#][#] /chatter | /addchatter | /removechatter commands
|   |   |   |       |   `-- chatters.py
|   |   |   |       |-- shiftloader                     [#][#] Shift loader
|   |   |   |       |   `-- shiftloader.py
|   |   |   |       |-- shifts                          [#][#] Some shift commands
|   |   |   |       |   |-- addshift                        [#][#] /addshift command
|   |   |   |       |   |   `-- addshift.py
|   |   |   |       |   |-- dayoff                          [#][#] /dayoff command
|   |   |   |       |   |   `-- dayoff.py
|   |   |   |       |   `-- swapshift                       [#][#] /swap command
|   |   |   |       |       `-- swapshift.py        
|   |   |   |       |-- subscription                    [#][#] /sub command
|   |   |   |       |   `-- subscription.py         
|   |   |   |       |-- webdav                          [#][#] /webdav command
|   |   |   |       |   `-- menu.py         
|   |   |   |       `-- workers                         [#][#] /workers command
|   |   |   |           `-- workers.py                  
|   |   |   |-- chattersmanager                     [#] Chatter manager
|   |   |   |   `-- chatters.py
|   |   |   |-- shiftmanager                        [#] Shift manager
|   |   |   |   |-- shift_changer.py
|   |   |   |   `-- shift_swapper.py
|   |   |   `-- workersmanager                      [#] Workers manager
|   |   |       |-- day_workers.py
|   |   |       `-- employees.py
|   |   `-- services                                [#] Services [#]
|   |       |-- webdav                                  [##] WebDAV service
|   |       |   |-- client.py
|   |       |   `-- server.py
|   |       |-- bot.py                                  [##] Bot service
|   |       |-- logger.py                               [##] Logger service
|   |       `-- subscription.py                         [##] Subscription service
|   `-- main.py                                     [#] Main file
|-- android_instruction.md
|-- README.md
`-- requirements.txt                                [#] Requirements for using
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
> JSON file with following format:
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
> JSON file with following format:
```
{
    "Employer_name_1" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)",
        "subscription": {
            "enabled": bool,
            "time_to_notify": "20:00"
        },
        "webdav": {
            "name": "Work",
            "url": "calendar_url",
            "password": "password"
        }
    },
    "Employer_name_2" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)",
        "subscription": {
            "enabled": bool,
            "time_to_notify": "20:00"
        },
        "webdav": {
            "name": "Work",
            "url": "calendar_url",
            "password": "password"
        }
    },
    .........
    "Employer_name_n" : {
        "telegram" : "Employer telegram",
        "telegram_id" : "Employer telegram id",
        "group" : "Employer group (ShopMaster/Poisk/CMS/LK)",
        "subscription": {
            "enabled": bool,
            "time_to_notify": "20:00"
        },
        "webdav": {
            "name": "Work",
            "url": "calendar_url",
            "password": "password"
        }
    }
    
}
```
