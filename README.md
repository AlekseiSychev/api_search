The provided usernames are checked on over 145 websites within few seconds.

## Features

* **Fast**, lookup can complete **under 20 seconds**
* Over **145** platforms are included
* Batch processing
    * GET request with data in browser address bar
    * POST request with data in Json
    * Return Json response with find Usernames and information about URLs

## Installation
    Note: Required python version is 3.7+
### Clone repository
    git clone https://github.com/AlekseiSychev/api_snoop.git

### Enter working directory
    $ cd ~/api_search

### Install python3 or python3-pip, if they are not installed
    $ apt-get update && apt-get install python3 python3-pip

### Install dependency 'requirements'
    $ pip install --upgrade pip
    $ python3 -m pip install -r requirements.txt

## Usage
    Run server on command line: uvicorn api:app --reload
    Open browser and follow http://127.0.0.1:8000/docs where you can test requests 

### GET request:

  #### Single username
    http://127.0.0.1:8000/username/Alex

  #### Several usernames separated *%* 
    http://127.0.0.1:8000/username/Mike%anny%joseph

### POST request:

  #### Single username
    json_parameters = 
                    {
                        "uname": "alex",
                        "listing": True,
                        "verbose": True,
                        "site_list": "3dnews%4gameforum%AG%Akniga",
                        "timeout": 10,
                        "print_found_only": True,
                        "no_func": True,
                        "reports": False,
                        "autoclean": False,
                        "cert": True,
                        "norm": False,
                        "quickly": True,
                    }

    http://127.0.0.1:8000/username_json , json=json_parameters

  #### Several usernames separated *%*
    json_parameters = 
                    {
                        "uname": "Mike%anny%joseph",
                        "listing": True,
                        "verbose": True,
                        "site_list": "3dnews%4gameforum%AG%Akniga",
                        "timeout": 10,
                        "print_found_only": True,
                        "no_func": True,
                        "reports": False,
                        "autoclean": False,
                        "cert": True,
                        "norm": False,
                        "quickly": True,
                    }

    http://127.0.0.1:8000/username_json , json=json_parameters


## Returned JSON
    {'uname(никнейм)':
        [
            {   'Ресурс': "3dnews",
                'Страна': "RU",
                'Url': "http://forum.3dnews.ru/",
                'Ссылка_на_профиль': "http://forum.3dnews.ru/member.php?username=alex",
                'Статус': "найден!",
                'Статус_http': 200,
                'Общее_замедление/сек': "нет",
                'Отклик/сек': "0,53",
                'Общее_время/сек': "0,61",
                'Сессия/Kb': "42",
            },
            {
                ....
            },
            ....
        ]
    ....
    }
## Required search parameters:
    uname - (str) nickname to search | example: alex or nickolas%michel%SAM

## Optional search parameters:

    'listing' and 'sorty' parameters are only used together:
        listing - (bool) output to the console of the sorted database
        sorty - (str) by site countries — "1", by site name — "2", all — "3"

    verbose - (bool) detailed verbalization (network and site testing with console output)

    'site_list', 'exclude_country', 'one_level', 'country' use only one parameter:
        site_list - (str) list of sites from the database to search | example: 3dnews%4gameforum%AG%Akniga
        exclude_country - (str) list of excluded countries in the search | example - us%ru%wr%kb%eu%tr%de
        one_level - (str) list of countries to search | example: us%ru%wr%kb%eu%tr%de
        country - (bool) sorting sites by country(EU, RU and etc.) 

    timeout - (int) server response timeout
    print_found_only - (bool) display in the console only found sites
    no_func - (bool) disables colors; flags; progress;

    reports - (bool) save found user pages to local html files
    autoclean - (bool) delete all html reports, clear space

    cert - (bool) checking certificates on servers
    headers - (str) using custom User-Agents headers | example: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 RuxitSynthetic/1.0 v8614745334095228442 t8093092299234304605 ath2653ab72 altpriv cvcv=2 smf=0
    quickly - (bool) repetitive flexible connections on failed resources without software slowdown
    db - (str) name of used database