from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from snoop import run

app = FastAPI()

## Модель валидации типов данных для POST запроса
class Item(BaseModel):
    uname: str # никнейм для поиска | пример: alex или nickolas%michel%SAM

    ## Параметры listing и sorty используются только вместе
    listing: Optional[bool] = False # вывод в консоль отсортированной базы данных по умолчанию False
    sorty: Optional[str] = None # по странам сайта — "1", по названию сайта — "2", all — "3"

    verbose: Optional[bool] = False # подробная верболизация по умолчанию False (тестирование сети и сайтов с выводом в консоль)

    ## ЧЕТЫРЕ НЕ СОВМЕСТИМЫХ МЕЖДУ СОБОЙ ПАРАМЕТРОВ(site_list, exclude_country, one_level, country, использовать только один):
    site_list: Optional[str] = None # строка(str) разделенная знаком '%' пример: 3dnews%4gameforum%AG%Akniga | список сайтов из базы данных по которым будет вестись поиск, по умолчанию None
    exclude_country: Optional[str] = None # строка(str) разделенная знаком '%' пример: us%ru%wr%kb%eu%tr%de | список исключаемых стран в поиске, по умолчанию None
    one_level: Optional[str] = None # строка(str) разделенная знаком '%' пример: us%ru%wr%kb%eu%tr%de | список стран по которым ведется поиск, по умолчанию None
    country: Optional[bool] = False # сортировка сайтов по странам(EU, RU и тд) перед поиском, по умолчанию False

    timeout: Optional[int] = 5 # время ожидания ответа от сервера во время поиска, по умолчанию (5 сек). Влияет на (продолжительность поиска,'Timeout ошибки') Вкл. эту опцию необходимо при медленном интернет соединении, чтобы избежать длительных зависаний
    print_found_only: Optional[bool] = True # отображение в консоли только найденных сайтов, по умолчанию True
    no_func: Optional[bool] = False # отключает цвета; звук; флаги; браузер; прогресс, по умолчанию True. Экономит ресурсы системы и ускоряет поиск

    reports: Optional[bool] = False # cохранять найденные странички пользователей в локальные html-файлы, по умолчанию False
    autoclean: Optional[bool] = False # удалить все отчеты, очистить место | по умолчанию True

    cert: Optional[bool] = False # проверка сертификатов на серверах, по умолчанию False даёт меньше ошибок и больше результатов при поиске nickname
    headers: Optional[str] = None # использование собственных заголовков User-Agents передавать строку(str), по умолчанию None | пример: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 RuxitSynthetic/1.0 v8614745334095228442 t8093092299234304605 ath2653ab72 altpriv cvcv=2 smf=0
    norm: Optional[bool] = False # переключатель режимов: SNOOPninja > нормальный режим > SNOOPninja. По_умолчанию (GNU/Linux full version) вкл 'режим SNOOPninja':
        # ускорение поиска ~25pct, экономия ОЗУ ~50pct, повторное 'гибкое' соединение на сбойных ресурсах.
        # Режим SNOOPninja эффективен только для Snoop for GNU/Linux full version.
        # По_умолчанию (в Windows) вкл 'нормальный режим'. В demo version переключатель режимов деактивирован, по умолчанию False
    quickly: Optional[bool] = True # тихий режим поиска. Промежуточные результаты не выводятся на печать. Повторные гибкие соединения на сбойных ресурсах без замедления ПО. Самый прогрессивный режим поиска (в разработке - не использовать)
    db: Optional[str] = None # str название базы данных(зашифрованной) пример: BDdemo_en | по умолчанию None
    
    ## Параметры сриншота
    screenshot: Optional[bool] = False # сохранение скриншотов локально в формате png и добавление в общий json строкой base64 | по умолчанию False
    screen_width: Optional[int] = 1920 # ширина скриншота в пикселях | по умолчанию 1920
    screen_height: Optional[int] = 1080 # высота скриншота в пикселях | по умолчанию 1080

@app.get('/username/{uname}')
def username(uname: str, listing: bool = False, sorty: str = None, verbose: bool = False, site_list: str = None, exclude_country: str = None, one_level: str = None, country: bool = False, timeout: int = 5, print_found_only: bool = True, no_func: bool = False, reports: bool = False, autoclean: bool = False, cert: bool = False, headers: str = None, norm: bool = False, quickly: bool = True, db: str = None, screenshot: bool = False, screen_width: int = 1920, screen_height: int = 1080):
    '''
    GET запрос для запуска программы поиска. Возвращает JSON : \n

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

    Обязательный параметр uname: \n
        127.0.0.1:8000/username/alex или 127.0.0.1:8000/username/alex%sam%michel
    Не обязательные параметры активируются по шаблону: \n
        127.0.0.1:8000/username/{uname}?{название параметра}={значение параметра}
    Если параметров несколько они разделяются знаком '%': \n
        127.0.0.1:8000/username/alex?{название параметра}={значение параметра}%{название параметра}={значение параметра}

    Не обязательные параметры: \n
        listing=false/true
        sorty=1/2/3
        verbose=false/true
        site_list=3dnews%4gameforum%AG%Akniga
        exclude_country=us%ru%wr%kb%eu%tr%de
        one_level=us%ru%wr%kb%eu%tr%de
        country=false/true
        timeout=5
        print_found_only=true/false
        no_func=false/true
        reports=false/true
        autoclean=false/true
        cert=false/true
        headers=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 RuxitSynthetic/1.0 v8614745334095228442 t8093092299234304605 ath2653ab72 altpriv cvcv=2 smf=0
        norm=false/true
        quickly=true/false
        db=BDdemo_en
        screenshot=false/true
        screen_width=1920
        screen_height=1080
    '''

    if '%' in uname:
        ulist = uname.split('%')
        if len(ulist) > 1:
            try:
                search_username = run(args_username=ulist, args_listing=listing, sortY=sorty, args_verbose=verbose, args_site_list=site_list, args_exclude_country=exclude_country, args_one_level=one_level, args_country=country, args_timeout=timeout, args_print_found_only=print_found_only, args_no_func=no_func, args_reports=reports, args_autoclean=autoclean, args_cert=cert, args_headerS=headers, args_norm=norm, args_quickly=quickly, args_db=db, args_screenshot=screenshot, screen_width=screen_width, screen_height=screen_height)
                return search_username
            except SystemExit as ex:
                raise HTTPException(status_code=400, detail=f'{ex}')
        else:
            raise HTTPException(status_code=400, detail='Bad Request. Usernames must be separated by % and count of names two or more. Example: http://127.0.0.1:8000/username/Alex%Nikol%Sam')
    else:
        uname = [uname]
        try:
            search_username = run(args_username=uname, args_listing=listing, sortY=sorty, args_verbose=verbose, args_site_list=site_list, args_exclude_country=exclude_country, args_one_level=one_level, args_country=country, args_timeout=timeout, args_print_found_only=print_found_only, args_no_func=no_func, args_reports=reports, args_autoclean=autoclean, args_cert=cert, args_headerS=headers, args_norm=norm, args_quickly=quickly, args_db=db, args_screenshot=screenshot, screen_width=screen_width, screen_height=screen_height)
            return search_username
        except SystemExit as ex:
            raise HTTPException(status_code=400, detail=f'{ex}')


@app.post('/username_json/')
def username_json(item: Item):
    '''
    POST запрос для запуска программы поиска. Возвращает JSON : \n

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

    Пример передаваемого в запрос json:

        json_parameters = {
            "uname": "alex%mick%anny",
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
            "screenshot": true
            "screen_width": 800
            "screen_height": 600
        }
    '''

    if '%' in item.uname:
        ulist = item.uname.split('%')
        if len(ulist) > 1:
            try:
                search_username = run(args_username=ulist, args_listing=item.listing, sortY=item.sorty, args_verbose=item.verbose, args_site_list=item.site_list, args_exclude_country=item.exclude_country, args_one_level=item.one_level, args_country=item.country, args_timeout=item.timeout, args_print_found_only=item.print_found_only, args_no_func=item.no_func, args_reports=item.reports, args_autoclean=item.autoclean,args_cert=item.cert, args_headerS=item.headers, args_norm=item.norm, args_quickly=item.quickly, args_db=item.db, args_screenshot=item.screenshot, screen_width=item.screen_width, screen_height=item.screen_height)
                return search_username
            except SystemExit as ex:
                raise HTTPException(status_code=400, detail=f'{ex}')
        else:
            raise HTTPException(status_code=400, detail='Bad Request. Usernames must be separated by % and count of names two or more. Example: http://127.0.0.1:8000/username/Alex%Nikol%Sam')
    else:
        uname = [item.uname]
        try:
            search_username = run(args_username=uname, args_listing=item.listing, sortY=item.sorty, args_verbose=item.verbose, args_site_list=item.site_list, args_exclude_country=item.exclude_country, args_one_level=item.one_level, args_country=item.country, args_timeout=item.timeout, args_print_found_only=item.print_found_only, args_no_func=item.no_func, args_reports=item.reports, args_autoclean=item.autoclean,args_cert=item.cert, args_headerS=item.headers, args_norm=item.norm, args_quickly=item.quickly, args_db=item.db, args_screenshot=item.screenshot, screen_width=item.screen_width, screen_height=item.screen_height)
            return search_username
        except SystemExit as ex:
            raise HTTPException(status_code=400, detail=f'{ex}')
