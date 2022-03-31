# Инструкция для:
### Браузера Google Chrome:
 - очистить папку (~/api_search/chrome), оставить только README.md
 - скачать и установить https://www.google.com/intl/ru_ru/chrome/
 - проверить версию браузера и скачать chromedriver для него
 - chromdriver положить в эту папку (~/api_search/chrome)
 - если будут проблемы с местонахождением драйвера, изменить путь к драйверу через переменную CHROME_WEBDRIVER_PATH в файле snoop.py

### Браузера Chromium:
 - очистить папку (~/api_search/chrome), оставить только README.md
 - скачать https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html и распаковать файлы в папку (~/api_search/chrome)
 - проверить версию браузера и скачать chromedriver для него, если в скачанном архиве отсутствует файл драйвера
 - chromdriver положить в эту папку (~/api_search/chrome)
 - расскоментировать строку options.binary_location = CHROMIUM_PATH в файле snoop.py
 - изменить путь к бинарному файлу chromium через переменную CHROMIUM_PATH в файле snoop.py
 - если будут проблемы с местонахождением драйвера, изменить путь к драйверу через переменную CHROME_WEBDRIVER_PATH в файле snoop.py