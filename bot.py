import requests
import csv
import io
from datetime import date, datetime, timedelta
import calendar
import telegram
import time


#inizialize constat data
file_id = '__SPREADSHEET_FILEID__'
codici = ['21054', '21011', '21012', '21013', '20105']
bot_token = '__TELEGRAM_BOT_TOKEN__'
bot_chatID = '@__TELEGRAM_CHAT_NAME__'
secInHr = 3600

def sheetToList (file_id):
    headers={}
    headers["User-Agent"]= "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0"
    headers["DNT"]= "1"
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    headers["Accept-Encoding"] = "deflate"
    headers["Accept-Language"]= "en-US,en;q=0.5"
    lines = []

    url = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv".format(file_id)

    #r has the text
    r = requests.get(url)

    sio = io.StringIO( r.text, newline=None)
    #reader keeps all the data
    reader = csv.reader(sio, dialect=csv.excel)
    return reader

def listToStr (reader):
    #get current date
    today = date.today()
    d = today.strftime("%d/%m/%Y")

    #set checkers
    primo = True
    vacanza = True

    #write fist text line
    chatStrTxt = calendar.day_name[today.weekday()]  + ' ' + today.strftime("%d %b, %Y") +  '\n\n'

    for row in reader:
        if primo:
            primo = False
        else:
            if (row[5] == d):
                vacanza = False
                trovato = False
                for c in codici:
                    if c in row[3]:
                        trovato = True
                        break
                if trovato:
                    str = 'Corso: ' + row[2] + '\nDocente: ' + row[1] + '\nCodice: ' + row[3] + '\nOrario inizio: ' + row[6] + '\nOrario fine: ' + row[7] + '\n<a href="' + row[8] + '">link lezione</a>\n\n'
                    chatStrTxt = chatStrTxt + str
    if vacanza:
        return None
    return chatStrTxt

def secTo7am ():
    now = datetime.now()
    tomorrow = datetime.now() + timedelta(1)
    secUntilMidnight = (tomorrow.replace(hour=0, minute=0, second=0, microsecond=0) - now).total_seconds()
    return (secUntilMidnight + secInHr * 5)


while True:
    #extact data
    reader = sheetToList(file_id)
    chatStr = listToStr(reader)

    #send data to the telegram bot
    if chatStr != None:
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=bot_chatID,
                 text=chatStr,
                 parse_mode=telegram.ParseMode.HTML)

    secRem = secTo7am()
    #sleep 'till 7am
    print('dormo per ', secRem, ' sec')
    time.sleep(secRem)

