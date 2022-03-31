# cd C:\Users\User\work\api_search; env\Scripts\activate; uvicorn api:app --reload;
# env\Scripts\activate
# uvicorn api:app --reload

import base64
import json
import locale

import networktest
import shutil
import glob
import os
import platform
import random
import re
import requests
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from collections import Counter
from colorama import Fore, Style, init

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession
from rich.progress import BarColumn, SpinnerColumn, TimeElapsedColumn, Progress
from rich.panel import Panel
from rich.style import Style as STL
from rich.console import Console
from rich.table import Table


Android = True if "arm" in platform.platform(aliased=True, terse=0) or "aarch64" in platform.platform(aliased=True, terse=0) else False

locale.setlocale(locale.LC_ALL, '')
init(autoreset=True)
console = Console()  # Инициализация консоли для дальнейшего вывода информации

vers, vers_code, demo_full = 'v1.3.2G', "s", "d"

print(f"""\033[36m
  ___|
\___ \  __ \   _ \   _ \  __ \  
      | |   | (   | (   | |   | 
_____/ _|  _|\___/ \___/  .__/  
                         _|    \033[0m \033[37m\033[44m{vers}\033[0m
""")

_sb = "build" if vers_code == 'b' else "source"
__sb = "demo" if demo_full == 'd' else "full"

if sys.platform == 'win32': OS_ = f"ru Snoop for Windows {_sb} {__sb}"
elif Android: OS_ = f"ru Snoop for Termux source {__sb}"
elif sys.platform != 'win32': OS_ = f"ru Snoop for GNU/Linux {_sb} {__sb}"

version = f"{vers}_{OS_}"


def DB(db_base):
    try:
        with open(db_base, "r", encoding="utf8") as f_r:
            db = f_r.read()
            db = db.encode("UTF-8")
            db = base64.b64decode(db)
            db = db[::-1]
            db = base64.b64decode(db)
            trinity = json.loads(db.decode("UTF-8"))
            return trinity
    except Exception:
        print(Style.BRIGHT + Fore.RED + "Упс, что-то пошло не так..." + Style.RESET_ALL)
        sys.exit('Bad database. Ошибка базы данных')


## Получаем результаты и в будущем везде используем, сокращая вызовы функций.
args_DB = 'BDdemo'
BDdemo = DB(args_DB)  # Выбираем базу данных для поиска
BDflag = DB('BDflag')

flagBS = len(BDdemo)

time_date = time.localtime()
censors = 0
censors_timeout = 0
recensor = 0

## Создание директорий результатов.
dirresults = os.getcwd()
dirhome = os.environ['HOME'] + "/snoop" if sys.platform != 'win32' else os.environ['LOCALAPPDATA'] + "\\snoop"
dirpath = dirresults if 'source' in version else dirhome
os.makedirs(f"{dirpath}/results", exist_ok=True)
os.makedirs(f"{dirpath}/results/nicknames/save reports", exist_ok=True)

CHROMIUM_PATH = f"{dirpath}/chrome/chrome.exe" # путь к бинарному файлу хромиум
CHROME_WEBDRIVER_PATH = f"{dirpath}/chrome/chromedriver.exe" # путь к веб-драйверу хром

################################################################################


class ElapsedFuturesSession(FuturesSession):
    def request(self, method, url, *args, **kwargs):
        return super(ElapsedFuturesSession, self).request(method, url, *args, **kwargs)


## Вывести на печать инфостроку.
def info_str(infostr, nick, color=True):
    if color is True:
        print(f"{Fore.GREEN}[{Fore.YELLOW}*{Fore.GREEN}] {infostr}{Fore.RED} <{Fore.WHITE} {nick} {Fore.RED}>{Style.RESET_ALL}")
    else:
        print(f"\n[*] {infostr} < {nick} >")


## Вывести на печать ошибки.
def print_error(websites_names, errstr, errX, verbose=False, color=True):
    if color is True:
        print(f"{Style.RESET_ALL}{Fore.RED}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.RED}]{Style.BRIGHT}"
              f"{Fore.GREEN} {websites_names}: {Style.BRIGHT}{Fore.RED}{errstr}{Fore.YELLOW} {errX if verbose else ''}")
    else:
        print(f"[!] {websites_names}: {errstr} {errX if verbose else ''}")


## Вывод на печать на разных платформах, индикация.
def print_found_country(websites_names, url, country_Emoj_Code, response_time=False, verbose=False, color=True):
    """Вывести на печать аккаунт найден."""
    if color is True and sys.platform == 'win32':
        print(f"{Style.RESET_ALL}{Style.BRIGHT}{Fore.CYAN}{country_Emoj_Code}"
              f"{Fore.GREEN}  {websites_names}:{Style.RESET_ALL}{Fore.GREEN} {url}")
    elif color is True and sys.platform != 'win32':
        print(f"{Style.RESET_ALL}{country_Emoj_Code}{Style.BRIGHT}{Fore.GREEN}  {websites_names}:"
              f"{Style.RESET_ALL}{Style.DIM}{Fore.GREEN}{url}")
    else:
        print(f"[+] {websites_names}: {url}")


def print_not_found(websites_names, verbose=False, color=True):
    """Вывести на печать аккаунт не найден."""
    if color is True:
        print(f"{Style.RESET_ALL}{Fore.CYAN}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.CYAN}]"
              f"{Style.BRIGHT}{Fore.GREEN} {websites_names}: {Style.BRIGHT}{Fore.YELLOW}Увы!")
    else:
        print(f"[-] {websites_names}: Увы!")


## Вывести на печать пропуск сайтов по блок. маске в имени username, gray_list, и пропуск по проблеме с openssl.
def print_invalid(websites_names, message, color=True):
    """Ошибка вывода nickname и gray list"""
    if color is True:
        print(f"{Style.RESET_ALL}{Fore.RED}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.RED}]"
              f"{Style.BRIGHT}{Fore.GREEN} {websites_names}: {Style.RESET_ALL}{Fore.YELLOW}{message}")
    else:
        print(f"[-] {websites_names}: {message}")


## Вернуть результат future for2.
# Логика: возврат ответа и дуб_метода в случае успеха, иначе возврат несуществующего метода для посл.работки.
def get_response(request_future, error_type, websites_names, print_found_only=False, verbose=False, color=True):
    try:
        res = request_future.result()
        if res.status_code:
            return res, error_type, res.elapsed
    except requests.exceptions.HTTPError as err1:
        if print_found_only is False:
            print_error(websites_names, "HTTP Error", err1, verbose, color)
    except requests.exceptions.ConnectionError as err2:
        global censors
        censors += 1
        if print_found_only is False:
            print_error(websites_names, "Ошибка соединения", err2, verbose, color)
    except requests.exceptions.Timeout as err3:
        global censors_timeout
        censors_timeout += 1
        if print_found_only is False:
            print_error(websites_names, "Timeout ошибка", err3, verbose, color)
    except requests.exceptions.RequestException as err4:
        if print_found_only is False:
            print_error(websites_names, "Непредвиденная ошибка", err4, verbose, color)
    return None, "Great Snoop returns None", -1


## Сохранение отчетов опция (-S).
def new_session(url, headers, session2, error_type, username, websites_names, r, t):
    future2 = session2.get(url=url, headers=headers, allow_redirects=True, timeout=t)
    response = future2.result()
    session_size = len(response.content)  # подсчет извлеченных данных
    with open(f"{dirpath}/results/nicknames/save reports/{username}/{websites_names}.html", 'w', encoding=r.encoding) as repre:
        repre.write(response.text)
    return response, session_size


def sreports(url, headers, session2, error_type, username, websites_names, r):
    os.makedirs(f"{dirpath}/results/nicknames/save reports/{username}", exist_ok=True)
    """Сохранять отчеты для метода: redirection."""

    if error_type == "redirection":
        try:
            response, session_size = new_session(url, headers, session2, error_type, username, websites_names, r, t=4)
        except requests.exceptions.ConnectionError:
            time.sleep(0.3)
            try:
                response, session_size = new_session(url, headers, session2, error_type, username, websites_names, r, t=2)
            except Exception:
                session_size = 'Err'  # подсчет извлеченных данных
        return session_size
    else:
        """Сохранять отчеты для всех остальных методов: status; response; message со стандартными параметрами."""
        with open(f"{dirpath}/results/nicknames/save reports/{username}/{websites_names}.html", 'w', encoding=r.encoding) as rep:
            rep.write(r.text)

def sscreen_chrome(url: str, path: str, website_name: str, index: int, width=1920, height=1080):
    """Настройка браузера и создание скриншота в формате png/base64

    Args:
        url (str): URL сайта для перехода методом get
        path (str): Путь сохранения скриншота в формате png
        website_name (str): Название вебсайта на который переходим
        index (int): Индекс словоря для дальнейшего преобразования
        width (int): Ширина скриншота
        height (int): Высота скриншота

    Returns:
        index (int): индекс словоря для дальнейшего присвоения ему строки 'screenshot': base64(str)
        screen_base64 (str): закодированния изображение в формате base64 
    """
    
    ## Создание User-Agent
    majR = random.choice(range(73, 94, 1))
    minR = random.choice(range(2683, 4606, 13))
    patR = random.choice(range(52, 99, 1))
    RandHead=[f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " + \
                f"Chrome/{majR}.0.{minR}.{patR} Safari/537.36",
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{majR}.0.{minR}.{patR} Safari/537.36"]
    user_agent = random.choice(RandHead)
    
    ## Настройки для браузера Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--hide-scrollbars")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.binary_location = CHROMIUM_PATH ## путь к бинарному файлу хромиум

    
    s = Service(executable_path=CHROME_WEBDRIVER_PATH) ## путь к веб-драйверу
    browser = webdriver.Chrome(options=options, service=s)
    browser.set_window_size(width, height)
    
    screen_base64 = "error"
    
    try:
        browser.get(url)
        browser.save_screenshot(f"{path}/{website_name}.png")
        screen_base64 = browser.get_screenshot_as_base64()
    except Exception as ex:
        pass
        # print(ex)
    finally:
        browser.quit()
    
    if screen_base64 != "error":
        msg = Fore.GREEN + f"{url} - сохранено"
    else:
        msg = Fore.RED + f"{url} - ошибка сохранения"
        
    return index, screen_base64, msg
    
def sscreenshot(username: str, info_urls_list: list, BDdemo_new, norm: bool, width: int, height: int):
    """Подготовка задач для многопоточного исполнения функции sscreen_chrome

    Args:
        username (str): Никнейм пользователя
        info_urls_list (list): Список словарей с данными сайтов
        BDdemo_new (_type_): База данных для выбора кол-ва потоков
        norm (bool): Параметр для выбора кол-ва потоков
        width (int): Ширина скриншота. Defaults to 1920
        height (int): Высота скриншота. Defaults to 1080

    Returns:
        info_urls_list (list): Измененный список словарей с добавленной строкой 'screenshot': base64(str)
    """
    
    date_screen = time.strftime('%d.%m.%Y', time_date)
    time_screen = time.strftime('%Hh %Mm %Ss', time_date)
    
    os.makedirs(f"{dirpath}/results/screenshots/{username}/{date_screen}/{time_screen}/", exist_ok=True)
    path = f"{dirpath}/results/screenshots/{username}/{date_screen}/{time_screen}"
    
    if sys.platform != 'win32':
        if Android:
            tread__ = len(BDdemo_new) if len(BDdemo_new) < 10 else 10
        else:  #linux
            if norm is False:
                tread__ = len(BDdemo_new) if len(BDdemo_new) < 16 else 16 
    else:  #windows
        tread__ = len(BDdemo_new) if len(BDdemo_new) < 14 else 14
    
    count_error = 0
    
    with ThreadPoolExecutor(max_workers=tread__) as executor:
        print(Fore.CYAN + f'Кол-во профилей для сохранения скриншота - {len(info_urls_list)}')
        futures = []
        for info_url_dict in info_urls_list:
            url = info_url_dict.get('Ссылка_на_профиль')
            website_name = info_url_dict.get('Ресурс')
            index = info_urls_list.index(info_url_dict)
            futures.append(executor.submit(sscreen_chrome, url, path, website_name, index, width, height))
        for future in as_completed(futures):
            index, screen_base64, msg = future.result()
            info_urls_list[index]["Screenshot"] = screen_base64 # запись в словарь скриншота в формате base64
            print(msg)
            if screen_base64 == "error":
                count_error += 1
    
    
    print(Fore.CYAN + f'Кол-во сохраненных скриншотов - {len(info_urls_list) - count_error} \n')
    
    return info_urls_list # измененный список со словарями
    
## Основная функция.
def snoop(username, BDdemo_new, verbose=False, country=False, norm=False, reports=False, print_found_only=False, timeout=None, color=True, cert=False, quickly=False, headerS=None):

    timestart = time.time()

# Печать первой инфостроки.
    if '%20' in username:
        username_space = re.sub("%20", " ", username)
        info_str("разыскиваем:", username_space, color)
    else:
        info_str("разыскиваем:", username, color)

    username = re.sub(" ", "%20", username)


## Предотвращение 'DDoS' из-за невалидных логинов; номеров телефонов, ошибок поиска из-за спецсимволов.
    with open('domainlist.txt', 'r', encoding="utf-8") as err:
        ermail = err.read().splitlines()

        username_bad = username.rsplit(sep='@', maxsplit=1)
        username_bad = '@bro'.join(username_bad).lower()

        for ermail_iter in ermail:
            if ermail_iter.lower() == username.lower():
                print(f"\n{Style.BRIGHT}{Fore.RED} Bad nickname: '{ermail_iter}' (поиск по email недоступен)")
                sys.exit('Bad nickname. Поиск по email недоступен')
            elif ermail_iter.lower() in username.lower():
                usernameR = username.rsplit(sep=ermail_iter.lower(), maxsplit=1)[1]
                username = username.rsplit(sep='@', maxsplit=1)[0]

                if len(username) == 0: username = usernameR
                print(f"\n{Fore.CYAN}Обнаружен E-mail адрес, извлекаем nickname: '{Style.BRIGHT}{Fore.CYAN}{username}{Style.RESET_ALL}" +
                      f"{Fore.CYAN}'\nsnoop способен отличать e-mail от логина, например, поиск '{username_bad}'\n" +
                      "не является валидной электропочтой, но может существовать как nickname, следовательно — не будет обрезан\n")

                if len(username) == 0 and len(usernameR) == 0:
                    print(f"\n{Style.BRIGHT}{Fore.RED} Bad nickname: '{ermail_iter}' (поиск по email недоступен)")
                    sys.exit('Bad nickname. Поиск по email недоступен')

        del ermail


    with open('specialcharacters', 'r', encoding="utf-8") as errspec:
        my_list_bad = list(errspec.read())
        if any(symbol_bad in username for symbol_bad in my_list_bad):
            console.print(f"[bold red]недопустимые символы в username: '{username}'\n\nВыход")
            sys.exit('Bad nickname. Недопустимые символы в username')


    ernumber = ['79', '89', "38", "37"]
    if any(ernumber in username[0:2] for ernumber in ernumber):
        if len(username) >= 10 and len(username) <= 13 and username.isdigit() is True:
            print(Style.BRIGHT + Fore.RED + "\nSnoop выслеживает учётки пользователей, но не номера телефонов...")
            sys.exit('Bad nickname. ПО выслеживает учётки пользователей, но не номера телефонов...')
    elif username[0] == "+" or username[0] == ".":
        print(Style.BRIGHT + Fore.RED + "\nПубличный логин, начинающийся с такого символа, практически всегда невалидный...")
        sys.exit('Bad nickname. Публичный логин, начинающийся с такого символа, практически всегда невалидный...')
    elif username[0] == "9" and len(username) == 10 and username.isdigit() is True:
        print(Style.BRIGHT + Fore.RED + "\nSnoop выслеживает учётки пользователей, но не номера телефонов...")
        sys.exit('Bad nickname. ПО выслеживает учётки пользователей, но не номера телефонов...')

    global nick
    nick = username  #username 2-переменные (args/info)


## Создать многопоточный/процессный сеанс для всех запросов.
    requests.packages.urllib3.disable_warnings()  #блокировка предупреждений о сертификате
    my_session = requests.Session()

    if cert is False:
        my_session.verify = False
        requests.packages.urllib3.disable_warnings()

    if sys.platform != 'win32':
        if Android:
            tread__ = len(BDdemo_new) if len(BDdemo_new) < 10 else 10
            session1 = ElapsedFuturesSession(executor=ThreadPoolExecutor(max_workers=tread__), session=my_session)
        else:  #linux
            if norm is False:
                proc_ = len(BDdemo_new) if len(BDdemo_new) < 26 else 26
                session1 = ElapsedFuturesSession(executor=ProcessPoolExecutor(max_workers=proc_), session=my_session)
            else:
                tread_ = len(BDdemo_new) if len(BDdemo_new) < 16 else 16
                session1 = ElapsedFuturesSession(executor=ThreadPoolExecutor(max_workers=tread_), session=my_session)   
    else:  #windows
        tread__ = len(BDdemo_new) if len(BDdemo_new) < 14 else 14
        session1 = ElapsedFuturesSession(executor=ThreadPoolExecutor(max_workers=tread__), session=my_session)

    if reports:
        session2 = FuturesSession(max_workers=1, session=my_session)
    if norm is False:
        session3 = ElapsedFuturesSession(executor=ThreadPoolExecutor(max_workers=1), session=my_session)
        
        
## Результаты анализа всех сайтов.
    dic_snoop_full = {}
## Создание futures на все запросы. Это позволит распараллелить запросы с прерываниями.
    for websites_names, param_websites in BDdemo_new.items():
        results_site = {}

        param_websites.pop('usernameON', None)
        param_websites.pop('usernameOFF', None)
        param_websites.pop('comments', None)

# Запись URL основного сайта и флага страны (сопоставление в БД).
        results_site['flagcountry'] = param_websites.get("country")
        results_site['flagcountryklas'] = param_websites.get("country_klas")
        results_site['url_main'] = param_websites.get("urlMain")

# Пользовательский user-agent браузера (рандомно на каждый сайт), а при сбое — постоянный с расширенным заголовком.
        majR = random.choice(range(73, 94, 1))
        minR = random.choice(range(2683, 4606, 13))
        patR = random.choice(range(52, 99, 1))
        RandHead=([f"{{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " + \
                   f"Chrome/{majR}.0.{minR}.{patR} Safari/537.36'}}",
                   f"{{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                   f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{majR}.0.{minR}.{patR} Safari/537.36'}}"])
        RH = random.choice(RandHead)
        headers = json.loads(RH.replace("'", '"'))

# Переопределить/добавить любые дополнительные заголовки, необходимые для данного сайта из БД или cli.
        if "headers" in param_websites:
            headers.update(param_websites["headers"])
        if headerS is not None:
            headers.update({"User-Agent": ''.join(headerS)})
        #console.print(headers, websites_names)  #проверка u-агентов

# Пропуск временно-отключенного сайта и не делать запрос, если имя пользователя не подходит для сайта.
        exclusionYES = param_websites.get("exclusion")
        if exclusionYES and re.search(exclusionYES, username) or param_websites.get("bad_site") == 1:
            if exclusionYES and re.search(exclusionYES, username) and not print_found_only:
                print_invalid(websites_names, f"недопустимый ник '{username}' для данного сайта", color)
            results_site["exists"] = "invalid_nick"
            results_site["url_user"] = '*' * 56
            results_site['countryCSV'] = "****"
            results_site['http_status'] = '*' * 10
            results_site['session_size'] = ""
            results_site['check_time_ms'] = '*' * 15
            results_site['response_time_ms'] = '*' * 15
            results_site['response_time_site_ms'] = '*' * 25
            if param_websites.get("bad_site") == 1 and verbose and not print_found_only:
                print_invalid(websites_names, "**Пропуск. Dynamic gray_list", color)
                results_site["exists"] = "gray_list"
            if param_websites.get("bad_site") == 1 and exclusionYES is None:
                results_site["exists"] = "gray_list"
        else:
# URL пользователя на сайте (если он существует).
            url = param_websites["url"].format(username)
            results_site["url_user"] = url
            url_API = param_websites.get("urlProbe")
# Использование api/nickname.
            url_API = url if url_API is None else url_API.format(username)

# Если нужен только статус кода, не загружать тело страницы, экономим память для status/redirect методов.
            if reports or param_websites["errorTypе"] == 'message' or param_websites["errorTypе"] == 'response_url':
                request_method = session1.get
            else:
                request_method = session1.head

# Сайт перенаправляет запрос на другой URL.
# Имя найдено. Запретить перенаправление чтобы захватить статус кода из первоначального url.
            if param_websites["errorTypе"] == "response_url" or param_websites["errorTypе"] == "redirection":
                allow_redirects = False
# Разрешить любой редирект, который хочет сделать сайт и захватить тело и статус ответа.
            else:
                allow_redirects = True

# Отправить параллельно все запросы и сохранить future in data для последующего доступа к хукам.
            future = request_method(url=url_API, headers=headers, allow_redirects=allow_redirects, timeout=timeout)
            param_websites["request_future"] = future
            #d2.update({future:{k:v}})
# Добавлять флаги/url-s/хуки в будущий-окончательный словарь с будущими всеми другими результатами.
        dic_snoop_full[websites_names] = results_site


# Прогресс_описание.
    if not verbose:
        if sys.platform != 'win32':
            progress = Progress(TimeElapsedColumn(), SpinnerColumn(spinner_name=random.choice(["dots", "dots12"])),
                                "[progress.percentage]{task.percentage:>1.0f}%", BarColumn(bar_width=None, complete_style='cyan',
                                finished_style='cyan bold'), refresh_per_second=3.0)  #transient=True) #исчезает прогресс
        else:
            progress = Progress(TimeElapsedColumn(), "[progress.percentage]{task.percentage:>1.0f}%", BarColumn(bar_width=None,
                                complete_style='cyan', finished_style='cyan bold'), refresh_per_second=3.0)  #auto_refresh=False)
    else:
        progress = Progress(TimeElapsedColumn(), "[progress.percentage]{task.percentage:>1.0f}%", auto_refresh=False)  #refresh_per_second=3


## Панель вербализации.
        if not Android:
            if color:
                console.print(Panel("[yellow]об.время[/yellow] | [magenta]об.% выполн.[/magenta] | [bold cyan]отклик сайта[/bold cyan] " + \
                                    "| [bold red]цвет.[bold cyan]об[/bold cyan].скор.[/bold red] | [bold cyan]разм.расп.данных[/bold cyan]",
                                    title="Обозначение", style=STL(color="cyan")))
            else:
                console.print(Panel("об.время | об.% выполн. | отклик сайта | цвет.об.время | разм.расп.данных", title="Обозначение"))
        else:
            if color:
                console.print(Panel("[yellow]time[/yellow] | [magenta]perc.[/magenta] | [bold cyan]response [/bold cyan] " + \
                                    "| [bold red]joint[bold cyan].[/bold cyan]rate[/bold red] | [bold cyan]data[/bold cyan]",
                                    title="Designation", style=STL(color="cyan")))
            else:
                console.print(Panel("time | perc. | response | joint.rate | data", title="Designation"))


## Пройтись по массиву future и получить результаты.
    li_time = [0]
    with progress:
        if color is True:
            task0 = progress.add_task("", total=len(BDdemo_new.items()))
        for websites_names, param_websites in BDdemo_new.items():  #БД:-скоррект.Сайт--> флаг,эмодзи,url, url_сайта, gray_lst, запрос-future
            if color is True:
                progress.update(task0, advance=1, refresh=True)  #\nprogress.refresh()
# Получить другую информацию сайта, снова.
            url = dic_snoop_full.get(websites_names).get("url_user")
            country_emojis = dic_snoop_full.get(websites_names).get("flagcountry")
            country_code = dic_snoop_full.get(websites_names).get("flagcountryklas")
            country_Emoj_Code = country_emojis if sys.platform != 'win32' else country_code
# Пропустить запрещенный никнейм или пропуск сайта из gray-list.
            if dic_snoop_full.get(websites_names).get("exists") is not None:
                continue
# Получить ожидаемый тип данных 4 методов.
            error_type = param_websites["errorTypе"]
# Получить результаты future.
            r, error_type, response_time = get_response(request_future=param_websites["request_future"], error_type=error_type,
                                                        websites_names=websites_names, print_found_only=print_found_only,
                                                        verbose=verbose, color=color)
# Повторное сбойное соединение через новую сессию быстрее, чем через adapter - timeout*2=дольше.
            if norm is False and quickly is False and r is None and 'raised ConnectionError' in str(future):
                #print(future)
                head_duble = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' + \
                                            'Chrome/76.0.3809.100 Safari/537.36'}

                for _ in range(3):
                    global recensor
                    recensor += 1
                    future_rec = session3.get(url=url, headers=head_duble, allow_redirects=allow_redirects, timeout=1.5)
                    if color is True and print_found_only is False:
                        print(f"{Style.RESET_ALL}{Fore.CYAN}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.CYAN}]" \
                              f"{Style.BRIGHT}{Fore.GREEN}    └──повторное соединение{Style.RESET_ALL}")
                    else:
                        if print_found_only is False:
                            print("повторное соединение")
                        #time.sleep(0.1)
                    r, error_type, response_time = get_response(request_future=future_rec, error_type=param_websites.get("errorTypе"),
                                                                websites_names=websites_names, print_found_only=print_found_only,
                                                                verbose=verbose, color=color)

                    if r is not None:
                        break


## Проверка, 4 методов; #1.
# Ответы message (разные локации).
            if error_type == "message":
                error = param_websites.get("errorMsg")
                error2 = param_websites.get("errоrMsg2")
                error3 = param_websites.get("errorMsg3") if param_websites.get("errorMsg3") is not None else "NoneNoneNone"
                if param_websites.get("errorMsg2"):
                    sys.exit('Error. method_1')
#                print(r.text) #проверка ответа (+- '-S')
#                print(r.status_code) #Проверка ответа
                if error2 in r.text or error in r.text or error3 in r.text:
                    if not print_found_only:
                        print_not_found(websites_names, verbose, color)
                    exists = "увы"
                else:
                    print_found_country(websites_names, url, country_Emoj_Code, response_time, verbose, color)
                    exists = "найден!"
                    if reports:
                        sreports(url, headers, session2, error_type, username, websites_names, r)
## Проверка, 4 методов; #2.
# Проверка username при статусе 301 и 303 (перенаправление и соль).
            elif error_type == "redirection":
#                print(r.text) #проверка ответа (+- '-S')
#                print(r.status_code) #Проверка ответа
                if r.status_code == 301 or r.status_code == 303:
                    print_found_country(websites_names, url, country_Emoj_Code, response_time, verbose, color)
                    exists = "найден!"
                    if reports:
                        session_size = sreports(url, headers, session2, error_type, username, websites_names, r)
                else:
                    if not print_found_only:
                        print_not_found(websites_names, verbose, color)
                        session_size = len(str(r.content))
                    exists = "увы"
## Проверка, 4 методов; #3.
# Проверяет, является ли код состояния ответа 2..
            elif error_type == "status_code":
#                print(r.text) #проверка ответа (+- '-S')
#                print(r.status_code) #Проверка ответа
                if not r.status_code >= 300 or r.status_code < 200:
                    print_found_country(websites_names, url, country_Emoj_Code, response_time, verbose, color)
                    if reports:
                        sreports(url, headers, session2, error_type, username, websites_names, r)
                    exists = "найден!"
                else:
                    if not print_found_only:
                        print_not_found(websites_names, verbose, color)
                    exists = "увы"
## Проверка, 4 методов; #4
# Перенаправление.
            elif error_type == "response_url":
#                print(r.text) #проверка ответа (+- '-S')
#                print(r.status_code) #Проверка ответа
                if 200 <= r.status_code < 300:
                    print_found_country(websites_names, url, country_Emoj_Code, response_time, verbose, color)
                    if reports:
                        sreports(url, headers, session1, error_type, username, websites_names, r)
                    exists = "найден!"
                else:
                    if not print_found_only:
                        print_not_found(websites_names, verbose, color)
                    exists = "увы"
## Если все 4 метода не сработали, например, из-за ошибки доступа (красный) или из-за неизвестной ошибки.
            else:
                exists = "блок"


## Попытка получить информацию из запроса.
            try:
                http_status = r.status_code  #запрос статус-кода.
            except Exception:
                http_status = "сбой"
            try:
                response_text = r.text.encode(r.encoding)  #запрос данных.
            except Exception:
                response_text = ""
            try:  # сессия в КБ
                if reports is True:
                    session_size = session_size if error_type == 'redirection' else len(str(r.content))
                else:
                    session_size = len(str(r.content))

                if session_size >= 555:
                    session_size = round(session_size / 1024)
                elif session_size <= 555:
                    session_size = round((session_size / 1024), 2)
            except Exception:
                session_size = "Err"


## Считать 2x-тайминги с приемлемой точностью.
# Реакция.
            ello_time = round(float(time.time() - timestart), 2)  #текущее
            li_time.append(ello_time)
            dif_time = round(li_time[-1] - li_time[-2], 2)  #разница
# Отклик.
            try:
                site_time = str(response_time).rsplit(sep=':', maxsplit=1)[1]
                site_time = round(float(site_time), 2)  #реальный ответ
            except Exception:
                site_time = str("-")


## Опция '-v'.
            if verbose is True:
                if session_size == 0 or session_size is None:
                    Ssession_size = "Head"
                elif session_size == "Err":
                    Ssession_size = "Нет"
                else:
                    Ssession_size = str(session_size) + " Kb"

                if color is True:
                    if dif_time > 2.7 and dif_time != ello_time:  #задержка в общем времени
                        console.print(f"[cyan] [*{site_time} s T] >>", f"[bold red][*{ello_time} s t]", f"[cyan][*{Ssession_size}]")
                        console.rule("", style="bold red")
                    else:
                        console.print(f"[cyan] [*{site_time} s T] >>", f"[cyan][*{ello_time} s t]", f"[cyan][*{Ssession_size}]")
                        console.rule("", style="bold blue")
                else:
                    console.print(f" [*{site_time} s T] >>", f"[*{ello_time} s t]", f"[*{Ssession_size}]", highlight=False)
                    console.rule(style="color")


## Служебная информация и для CSV (2-й словарь 'объединение словарей', чтобы не вызывать ошибку длины 1го при итерациях).
            if dif_time > 2.7 and dif_time != ello_time:
                dic_snoop_full.get(websites_names)['response_time_site_ms'] = str(dif_time)
            else:
                dic_snoop_full.get(websites_names)['response_time_site_ms'] = "нет"
            dic_snoop_full.get(websites_names)['exists'] = exists
            dic_snoop_full.get(websites_names)['session_size'] = session_size
            dic_snoop_full.get(websites_names)['countryCSV'] = country_code
            dic_snoop_full.get(websites_names)['http_status'] = http_status
            dic_snoop_full.get(websites_names)['check_time_ms'] = str(site_time)
            dic_snoop_full.get(websites_names)['response_time_ms'] = str(ello_time)
# Добавление результатов этого сайта в окончательный словарь со всеми другими результатами.
            dic_snoop_full[websites_names] = dic_snoop_full.get(websites_names)
# Вернуть словарь со всеми данными на запрос функции snoop.
        return dic_snoop_full

## Удаление отчетов.
def autoclean():
# Определение директорий.
    path_build_del = "/results" if sys.platform != 'win32' else "\\results"
    rm = dirpath + path_build_del
# Подсчет файлов и размера удаляемого каталога 'results'.
    total_size = 0
    delfiles = []
    for total_file in glob.iglob(rm + '/**/*', recursive=True):
        total_size += os.path.getsize(total_file)
        if os.path.isfile(total_file): delfiles.append(total_file)
# Удаление каталога 'results'.
    try:
        shutil.rmtree(rm, ignore_errors=True)
        print(f"\033[31;1mdeleted --> {rm}\033[0m\033[36m {len(delfiles)} files, {round(total_size/1024/1024, 2)} Mb\033[0m")
    except Exception:
        console.log("[red]Ошибка")
    sys.exit('Directory clean. Директория с результатами очищена')

## ОСНОВА.
def run(*, args_username, args_listing=False, sortY=None, args_verbose=False, args_site_list=None, args_exclude_country=None, args_one_level=None, args_country=False, args_timeout=5, args_print_found_only=True, args_no_func=True, args_reports=False, args_autoclean=False, args_cert=False, args_headerS=None, args_norm=False, args_quickly=True, args_db=None, args_screenshot=False, screen_width=1920, screen_height=1080):
    '''Параметры передаваемые в функцию run:
    args_listing - вывод в консоль отсортированной базы данных по умолчанию False | доп параметр переменная sortY = '' , по странам сайта — "1", по названию сайта — "2", all — "3"
    args_username - список(list) передаваемых имен для поиска
    args_verbose - подробная верболизация по умолчанию False (тестирование сети и сайтов с выводом в консоль)
    
    НЕ СОВМЕСТИМЫЕ МЕЖДУ СОБОЙ ПАРАМЕТРЫ(использовать только один):
        args_site_list - список сайтов ["3dnews", "4gameforum", "AG", "Akniga"] по которым будет вестись поиск, по умолчанию None
        args_exclude_country - список исключаемых стран в поиске ['us', 'ru', 'wr', 'kb', 'eu', 'tr', 'de' ], по умолчанию None
        args_one_level - список стран по которым ведется поиск ['ru', 'us']
        args_country - сортировка сайтов по странам(EU, RU и тд) перед поиском, по умолчанию False
    
    args_timeout - время ожидания ответа от сервера во время поиска, по умолчанию 5 сек. Влияет на(продолжительность поиска,'Timeout ошибки') Вкл. эту опцию необходимо при медленном интернет соединении, чтобы избежать длительных зависаний 
    args_print_found_only - отображение в консоли только найденных сайтов, по умолчанию True
    args_no_func - отключает цвета; звук; флаги; браузер; прогресс, по умолчанию True. Экономит ресурсы системы и ускоряет поиск
    args_reports - сохранение отчетов в файл, по умолчанию False
    args_autoclean - удалить все отчеты, очистить место | по умолчанию False
    args_cert - проверка сертификатов на серверах, по умолчанию False даёт меньше ошибок и больше результатов при поиске nickname
    args_headerS - использование собственных заголовков User-Agents передавать строку(str), по умолчанию None
    args_norm - переключатель режимов: SNOOPninja > нормальный режим > SNOOPninja. По_умолчанию (GNU/Linux full version) вкл 'режим SNOOPninja':
        ускорение поиска ~25pct, экономия ОЗУ ~50pct, повторное 'гибкое' соединение на сбойных ресурсах.
        Режим SNOOPninja эффективен только для Snoop for GNU/Linux full version.
        По_умолчанию (в Windows) вкл 'нормальный режим'. В demo version переключатель режимов деактивирован, по умолчанию False
    args_quickly - тихий режим поиска. Промежуточные результаты не выводятся на печать. Повторные гибкие соединения на сбойных ресурсах без замедления ПО. Самый прогрессивный режим поиска (в разработке - не использовать)
    args_db - str название базы данных(зашифрованной) | по умолчанию None
    args_screenshot - сохранение скриншотов локально в формате png и добавление в общий json строкой base64 | по умолчанию False
    screen_width - ширина скриншота в пикселях | по умолчанию 1920
    screen_height - высота скриншота в пикселях | по умолчанию 1080
    '''

## Опции  '-cseo' несовместимы между собой.
    k = 0
    for _ in bool(args_site_list), bool(args_country), bool(args_exclude_country), bool(args_one_level):
        if _ is True:
            k += 1
        if k == 2:
            print("опциии ['-c', '-e' '-o', '-s'] несовместимы между собой")

## Опция  '-a'.
    if args_autoclean:
        print(Fore.CYAN + "[+] активирована опция '-a': «удаление накопленных отчетов»")
        autoclean()

## Опция  '-H'.
    if args_headerS:
        print(f"{Fore.CYAN}[+] активирована опция '-H': «переопределение user-agent(s)»:" + '\n' + \
              f"    user-agent: '{Style.BRIGHT}{Fore.CYAN}{''.join(args_headerS)}{Style.RESET_ALL}{Fore.CYAN}'")

## Опция  '-f' + "-v".
    if args_verbose is True and args_print_found_only is True:
        print("Режим подробной вербализации [опция '-v'] отображает детальную информацию,\n   [опция '-f'] неуместна")

## Опция  '-С'.
    if args_cert:
        sumbol = "выкл" if Android else "вкл"
        print(Fore.CYAN + f"[+] активирована опция '-C': «проверка сертификатов на серверах {sumbol}»")

## Опция режима SNOOPnina > < нормальный режим.
    if args_norm is False:
        print(Fore.RED + "[-] в demo деактивирован переключатель '--': «режимов SNOOPninja/Normal»")

## Опция  '-S'.
    if args_reports:
        print(Fore.CYAN + "[+] активирована опция '-S': «сохранять странички найденных аккаунтов»")

## Опция  '-n'.
    if args_no_func:
        print(Fore.CYAN + "[+] активирована опция '-n': «отключены:: цвета; звук; флаги; браузер; прогресс»")

## Опция '-Ss'.
    if args_screenshot:
        print(Fore.CYAN + "[+] активирована опция '-Ss': «сохранение скриншотов профилей в формате png/base64»")

## Опция  '-t'.

    if args_timeout:
        args_timeout = abs(args_timeout)
        if args_timeout > 0:
            print(Fore.CYAN + f"[+] активирована опция '-t': «snoop будет ожидать ответа от " + \
                f"сайта \033[36;1m {args_timeout}_sec\033[0m\033[36m» \033[0m")


## Опция '-f'.
    if args_print_found_only:
        print(Fore.CYAN + "[+] активирована опция '-f': «выводить на печать только найденные аккаунты»")

## Опция '-s'.
    if args_site_list:
        args_site_list = args_site_list.split('%')
        print(f"{Fore.CYAN}[+] активирована опция '-s': «поиск '{Style.BRIGHT}{Fore.CYAN}{', '.join(args_username)}{Style.RESET_ALL}" + \
              f"{Fore.CYAN}' на выбранных website(s)»\n" + \
              f"    допустимо использовать опцию '-s' несколько раз\n" + \
              f"    [опция '-s'] несовместима с [опциями '-с', '-e', 'o']")

## Опция '--list-all'.
    if args_listing and sortY != None:
        print(Fore.CYAN + "[+] активирована опция '-l': «детальная информация о БД snoop»")
        print("\033[36m\nСортировать БД Snoop по странам, по имени сайта или обобщенно ?\n" + \
              "по странам —\033[0m 1 \033[36mпо имени —\033[0m 2 \033[36mall —\033[0m 3\n")

# Общий вывод стран (3!).
# Вывод для full/demo version.
        def sort_list_all(DB, fore, version, line=None):
            listfull = []
            if sortY == "3":
                if line == "str_line":
                    console.rule("[cyan]Ok, print All Country:", style="cyan bold")
                print("")
                li = [DB.get(con).get("country_klas") if sys.platform == 'win32' else DB.get(con).get("country") for con in DB]
                cnt = str(Counter(li))
                try:
                    flag_str_sum = (cnt.split('{')[1]).replace("'", "").replace("}", "").replace(")", "")
                    all_ = str(len(DB))
                except Exception:
                    flag_str_sum = str("БД повреждена.")
                    all_ = "-1"
                table = Table(title=Style.BRIGHT + fore + version + Style.RESET_ALL, style="green")
                table.add_column("Страна:Кол-во websites", style="magenta", justify='full')
                table.add_column("All", style="cyan", justify='full')
                table.add_row(flag_str_sum, all_)
                console.print(table)

# Сортируем по алфавиту для full/demo version (2!).
            elif sortY == "2":
                if line == "str_line":
                    console.rule("[cyan]Ok, сортируем по алфавиту:", style="cyan bold")
                if version == "demo version":
                    console.print('\n', Panel.fit("++База данных++", title=version, style=STL(color="cyan", bgcolor="red")))
                else:
                    console.print('\n', Panel.fit("++База данных++", title=version, style=STL(color="cyan")))
                i = 0
                sorted_dict_v_listtuple = sorted(DB.items(), key=lambda x: x[0].lower())  #сорт.словаря по глав.ключу без учета регистра
                datajson_sort = dict(sorted_dict_v_listtuple)  #преобр.список обратно в словарь (сортированный)

                for con in datajson_sort:
                    S = datajson_sort.get(con).get("country_klas") if sys.platform == 'win32' else datajson_sort.get(con).get("country")
                    i += 1
                    #print(f"{Style.DIM}{Fore.CYAN}{i}. {Style.RESET_ALL}{Fore.CYAN}{S}  {con}\n================")  #дорого
                    listfull.append(f"\033[36;2m{i}.\033[0m \033[36m{S}  {con}")
                print("\n================\n".join(listfull))

# Сортируем по странам для full/demo version (1!).
            elif sortY == "1":
                listwindows = []

                if line == "str_line":
                    console.rule("[cyan]Ok, сортируем по странам:", style="cyan bold")

                for con in DB:
                    S = DB.get(con).get("country_klas") if sys.platform == 'win32' else DB.get(con).get("country")
                    listwindows.append(f"{S}  {con}\n")

                if version == "demo version":
                    console.print('\n', Panel.fit("++База данных++", title=version, style=STL(color="cyan", bgcolor="red")))
                else:
                    console.print('\n', Panel.fit("++База данных++", title=version, style=STL(color="cyan")))

                for i in enumerate(sorted(listwindows, key=str.lower), 1):
                    #print(f"{Style.DIM}{Fore.CYAN}{i[0]}. {Style.RESET_ALL}{Fore.CYAN}{i[1]}", end='')  #дорого
                    listfull.append(f"\033[36;2m{i[0]}. \033[0m\033[36m{i[1]}")
                print("================\n".join(listfull))

# Действие не выбрано '--list-all'.
            else:
                print(Style.BRIGHT + Fore.RED + "└──Извините, но вы не выбрали действие [1/2/3]\n\nВыход")
                sys.exit('Module error. Действие 1/2/3 не выбрано')

# Запуск функции '--list-all'.
        if sortY != "3":
            sort_list_all(BDflag, Fore.GREEN, "full version", line="str_line")
            sort_list_all(BDdemo, Fore.RED, "demo version")
        else:
            sort_list_all(BDdemo, Fore.RED, "demo version", line="str_line")
            sort_list_all(BDflag, Fore.GREEN, "full version")

## Работа с базой.
## Опция  '-c'. Сортировка по странам.
    if args_country:
        print(Fore.CYAN + "[+] активирована опция '-c': «сортировка/запись результатов по странам»")
        country_sites = sorted(BDdemo, key=lambda k: ("country" not in k, BDdemo[k].get("country", sys.maxsize)))
        sort_web_BDdemo_new = {}
        for site in country_sites:
            sort_web_BDdemo_new[site] = BDdemo.get(site)

## Функция для опций '-eo'.
    def one_exl(one_exl_, bool_):
        lap = []
        bd_flag = []

        for k, v in BDdemo.items():
            bd_flag.append(v.get('country_klas').lower())
            if all(item.lower() != v.get('country_klas').lower() for item in one_exl_) is bool_:
                BDdemo_new[k] = v

        enter_coun_u = [x.lower() for x in one_exl_]
        lap = list(set(bd_flag) & set(enter_coun_u))
        diff_list = list(set(enter_coun_u) - set(bd_flag))  #вывести уник элем из enter_coun_u иначе set(enter_coun_u)^set(bd_flag)
        
        if bool(BDdemo_new) is False:
            print(f"\033[31;1m[{str(diff_list).strip('[]')}] все регионы поиска являются невалидными.\033[0m")
            sys.exit('Bad country. Все регионы поиска являются невалидными')
            
# Вернуть корректный и bad списки пользовательского ввода в cli.
        return lap, diff_list

## Если опции '-seo' не указаны, то используем БД, как есть.
    BDdemo_new = {}
    if args_site_list is None and args_exclude_country is None and args_one_level is None:
        if args_db is None: # проверка на другую базу данных
            BDdemo_new = BDdemo
        else:
            global args_DB
            args_DB = args_db
            print(Fore.CYAN + "[+] активирована опция '-db':" f'«Выбрана другая база данных: {args_db}»')
            BDdemo_new = BDdemo

## Опция '-s'.
    elif args_site_list is not None:
# Убедиться, что сайты в базе имеются, создать для проверки сокращенную базу данных сайта(ов).
        for site in args_site_list:
            for site_yes in BDdemo:
                if site.lower() == site_yes.lower():
                    BDdemo_new[site_yes] = BDdemo[site_yes]  #выбираем в словарь найденные сайты из БД

            diff_k_bd = set(BDflag) ^ set(BDdemo)
            for site_yes_full_diff in diff_k_bd:
                if site.lower() == site_yes_full_diff.lower():  #если сайт (-s) в БД Full версии
                    print(f"\033[31;1m[?] Пропуск:\033[0m \033[36mсайт из БД \033[36;1mfull-версии\033[0m \033[36mнедоступен в" + \
                          f"\033[0m \033[33;1mdemo-версии\033[0m\033[36m:: '\033[30;1m{site_yes_full_diff}\033[0m\033[36m'\033[0m")

            if not any(site.lower() == site_yes_full.lower() for site_yes_full in BDflag):  #если ни одного совпадения по сайту
                print(f"\033[31;1m[!] Пропуск:\033[0m \033[36mжелаемый сайт отсутствует в БД Snoop:: '" + \
                      f"\033[31;1m{site}\033[0m\033[36m'\033[0m")
# Отмена поиска, если нет ни одного совпадения по БД и '-s'.
        if not BDdemo_new:
            sys.exit('Bad database. Нет ни одного совпадения по БД')

## Опция '-e'.
# Создать для проверки сокращенную базу данных сайта(ов).
# Создать и добавить в новую БД сайты, аргументы (-e) которых != бук.кодам стран (country_klas).
    elif args_exclude_country is not None:
        args_exclude_country = args_exclude_country.split('%') # преобразование str в list
        lap, diff_list = one_exl(one_exl_=args_exclude_country, bool_=True)

        print(Fore.CYAN + f"[+] активирована опция '-e': «исключить из поиска выбранные регионы»::", end=' ')
        print(Style.BRIGHT + Fore.CYAN + str(lap).strip('[]').upper() + Style.RESET_ALL + " " + Style.BRIGHT + Fore.RED + \
              str(diff_list).strip('[]') + Style.RESET_ALL + Fore.CYAN + "\n" + \
              "    допустимо использовать опцию '-e' несколько раз\n" + \
              "    [опция '-e'] несовместима с [опциями '-s', '-c', 'o']")

## Опция '-o'.
# Создать для проверки сокращенную базу данных сайта(ов).
# Создать и добавить в новую БД сайты, аргументы (-e) которых != бук.кодам стран (country_klas).
    elif args_one_level is not None:
        args_one_level = args_one_level.split('%') # преобразование str в list
        lap, diff_list = one_exl(one_exl_=args_one_level, bool_=False)

        print(Fore.CYAN + f"[+] активирована опция '-o': «включить в поиск только выбранные регионы»::", end=' ')
        print(Style.BRIGHT + Fore.CYAN + str(lap).strip('[]').upper() + Style.RESET_ALL + " " + Style.BRIGHT + Fore.RED + \
              str(diff_list).strip('[]') + Style.RESET_ALL + Fore.CYAN + "\n" + \
              "    допустимо использовать опцию '-o' несколько раз\n" + \
              "    [опция '-o'] несовместима с [опциями '-s', '-c', 'e']")

## Опция '-v'.
    if args_verbose and bool(args_username):
        print(Fore.CYAN + "[+] активирована опция '-v': «подробная вербализация в CLI»\n")
        networktest.nettest()

## Опция  '-w' не активна.
    print(f"\n{Fore.CYAN}Загружена локальная база: {Style.BRIGHT}{Fore.CYAN}{len(BDdemo)}_Websites{Style.RESET_ALL}")

## Крутим user's.
    def starts(SQ):
        JSON = {}
        kef_user = 0
        
        for username in SQ:
            time_start_search = time.time()
            if username == '' or username == ' ': # Пропуск юзера если никнейм не содержит символов
                continue
            
            kef_user += 1
            sort_sites = sort_web_BDdemo_new if args_country is True else BDdemo_new

            FULL = snoop(username, sort_sites, country=args_country, verbose=args_verbose, cert=args_cert,
                        norm=args_norm, reports=args_reports, print_found_only=args_print_found_only, timeout=args_timeout,
                        color=not args_no_func, quickly=args_quickly, headerS=args_headerS)
            
            ungzip, ungzip_all, info_urls_list = [], [], []
            ## ОСНОВНОЙ цикл с подготовкой информации для вывода в JSON
            for site in FULL:
                dictionary = FULL[site]
                if dictionary.get('session_size') == 0:
                    Ssession = "Head"
                elif type(dictionary.get('session_size')) != str:
                    ungzip.append(dictionary.get('session_size')), ungzip_all.append(dictionary.get('session_size'))
                    Ssession = str(dictionary.get('session_size')).replace('.', locale.localeconv()['decimal_point'])
                else:
                    Ssession = "Bad"

                if dictionary.get('exists') == 'найден!':
                    if dictionary.get('http_status') == 200:
                        url_info_dict = {'Ресурс': site, 
                                        'Страна': dictionary.get('countryCSV'), 
                                        'Url': dictionary.get('url_main'), 
                                        'Ссылка_на_профиль': dictionary.get('url_user'), 
                                        'Статус': dictionary.get('exists'),
                                        'Статус_http': dictionary.get('http_status'), 
                                        'Общее_замедление/сек': dictionary.get('response_time_site_ms').replace('.', locale.localeconv()['decimal_point']), 
                                        'Отклик/сек': dictionary.get('check_time_ms').replace('.', locale.localeconv()['decimal_point']), 
                                        'Общее_время/сек': dictionary.get('response_time_ms').replace('.', locale.localeconv()['decimal_point']), 
                                        'Сессия/Kb': Ssession, 
                                        }
                                        
                        info_urls_list.append(url_info_dict) # добавляем в список со словарями найденную информацией по сайтам
                        
            ## Скриншот профиля на веб странице в формате png/base64          
            if args_screenshot:
                info_urls_list = sscreenshot(username, info_urls_list, BDdemo_new, norm=args_norm, width=screen_width, height=screen_height)
            
            dict_json = {username: info_urls_list}
            JSON.update(dict_json)
            
            # Размер сессии персональный и общий, кроме CSV.     
            try:
                s_size_all = round(sum(ungzip_all) / 1024, 2)  #в МБ
            except Exception:
                s_size_all = "Err"
                
            censors_cor = int((censors - recensor) / kef_user)  #err_connection
            censors_timeout_cor = int(censors_timeout / kef_user)  #err time-out
            flagBS_err = round((censors_cor + censors_timeout_cor) * 100 / flagBS, 3)
            time_all_search = str(round(time.time() - time_start_search))
            
            
## Финишный вывод.
            if bool(FULL) is True:
                if Android:
                    recomend = "       \033[36m├─используйте \033[36;1mVPN\033[0m \033[36m\n       ├─или увеличьте значение опции" + \
                            "'\033[36;1m-t\033[0m\033[36m'\n       └─или используйте опцию '\033[36;1m-C\033[0m\033[36m'\033[0m\n"
                else:
                    recomend = "       \033[36m├─используйте \033[36;1mVPN\033[0m \033[36m\n       └─или увеличьте значение опции" + \
                            "'\033[36;1m-t\033[0m\033[36m'"
                            
                print(f"{Fore.CYAN}├─Результаты:{Style.RESET_ALL} найдено --> {len(info_urls_list)} url (сессия: {time_all_search}сек | размер: {s_size_all}Mb)")

                if flagBS_err >= 2:  #perc
                    print(f"{Fore.CYAN}├───Дата поиска:{Style.RESET_ALL} {time.strftime('%d/%m/%Y_%H:%M:%S', time_date)}")
                    print(f"{Fore.CYAN}└────\033[31;1mВнимание! Bad_raw: {flagBS_err}% БД\033[0m")
                    print(f"{Fore.CYAN}     └─нестабильное соединение или I_Censorship")
                    print(recomend)
                else:
                    print(f"{Fore.CYAN}└───Дата поиска:{Style.RESET_ALL} {time.strftime('%d/%m/%Y_%H:%M:%S', time_date)}\n")
                
        ## Отправка Json в api.py 
        return JSON

## поиск по выбранным пользователям в такой последовательности:
    # run() --> starts() --> snoop()
    
    return starts(args_username)