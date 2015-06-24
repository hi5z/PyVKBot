import vk
import re
import sys
import time
import json
import socket
import random
import requests
import linecache
import urllib.parse
import configparser
import urllib.request


def printexception(botvkid):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    requests.post("http://bot.mew.su/service/listenerror.php",
                  data={'botid': botvkid,
                        'text': 'LINE {} "{}"): {}'.format(lineno,
                                                           line.strip(),
                                                           exc_obj)},
                  verify=False)


version = '0.0.3.1'

# Берем данные из конфига
config = configparser.ConfigParser()
config.read('config.ini')

# Inputs and shit
if (config['main']['token']) and (config['main']['botid']):
    print("Прошлые данные были восстановлены. Если желаете их изменить - отредактируйте config.ini")
    at = config['main']['token']
    bid = config['main']['botid']
elif (config['main']['token'] == '') and (config['main']['botid'] == ''):
    at = input("Введите свой ACCESS_TOKEN (о том как его получить - http://bot.mew.su):")
    bid = input("Введите ID своего бота с сайта iii.ru (или оставьте пустым для использования бота VIU-PIU):")
    # Пишем в файл
    config.set('main', 'token', at)
    config.set('main', 'botid', bid)
elif config['main']['token'] == '':
    at = input("Введите свой ACCESS_TOKEN (о том как его получить - http://bot.mew.su):")
    bid = config['main']['botid']
    # Пишем в файл
    config.set('main', 'token', at)
elif config['main']['botid'] == '':
    at = config['main']['token']
    bid = input("Введите ID своего бота с сайта iii.ru (или оставьте пустым для использования бота VIU-PIU):")

    if bid == '':
        bid = '[DEFAULT]'
    # Пишем в файл
    config.set('main', 'botid', bid)
else:
    at = config['main']['token']
    bid = config['main']['botid']

with open('config.ini', 'w') as configfile:
    config.write(configfile)

vkapi = vk.API(access_token=at)
jsn = vkapi.users.get().pop()
firstname = str(jsn['first_name'])

# TEST AREA

#

i = 0
while True:  # Infinite loop
    try:
        if i == 0:
            # TODO: Проверка старых неотвеченых сообщений
            longpoll = vkapi.messages.getLongPollServer(need_pts=1, use_ssl=0)
            ts1 = longpoll['ts']
            pts1 = longpoll['pts']
            print("Принимаем сообщения...")
        else:
            time.sleep(1)
            longpoll = vkapi.messages.getLongPollServer(need_pts=1, use_ssl=0)
            ts1 = longpoll['ts']
            pts1 = newpts['new_pts']

        newpts = vkapi.messages.getLongPollHistory(pts=pts1, ts=ts1)

        if i % 30 == 0:
            vkapi.account.setOnline(voip=0)
        # print(newpts)
        i += 1

        if not len(newpts['profiles']) == 0:
            info = newpts['profiles'].pop()
            history = newpts['messages']['items']

            parseitems = json.loads(json.dumps(history))
            jshistory = newpts

            inte = 0
            while inte < newpts['messages']['count']:
                if 'chat_id' not in parseitems[inte]:

                    if parseitems[inte]['out'] == 0:

                        # ЭТА ЧАСТЬ ДЛЯ ПЕРСОНАЛЬНОГО ЧАТА
                        showme = re.search(r'(покажи|как выглядит)\s(.*)?[\?]', parseitems[inte]['body'],
                                           re.IGNORECASE)
                        kurs = re.search(r'курс', parseitems[inte]['body'], re.IGNORECASE)
                        infa = re.search(r'(сколько инфа|какая вероятность|какова вероятность)[ того]?\s(.*)',
                                         parseitems[inte]['body'], re.IGNORECASE)
                        iliili = re.search(r'(.*)\s(или)(.*)?\?', parseitems[inte]['body'], re.IGNORECASE)

                        if bool(showme):
                            text = urllib.parse.quote(showme.group(2))
                            jsondata = urllib.request.urlopen(
                                "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&userip="
                                + socket.gethostname() +
                                "&rsz=1&safe=off&imgsz=large&q="
                                + text +
                                "&start=0")
                            decoded = json.loads(jsondata.readall().decode('utf-8'))
                            dec = decoded['responseData']['results'].pop()
                            urllib.request.urlretrieve(dec['unescapedUrl'], "images/attach.jpg")
                            photoserver = vkapi.photos.getMessagesUploadServer()
                            photo = {'photo': ('images/attach.jpg', open('images/attach.jpg', 'rb'))}
                            r = requests.post(photoserver['upload_url'], files=photo, verify=False)
                            rjs = json.loads(r.text)
                            attachment = vkapi.photos.saveMessagesPhoto(photo=rjs['photo'], server=rjs['server'],
                                                                        hash=rjs['hash']).pop()
                            phrases = (["Я думаю это то, что ты искал по запросу %s",
                                        "Я на правильном пути? %s это картинка ниже?", "Это оно? %s?",
                                        "Я считаю что вот то, что тебе нужно. Запрос: %s", "%s - вот же"])
                            random.shuffle(phrases)

                            vkapi.messages.setActivity(user_id=info['id'], type="typing")
                            time.sleep(2)
                            vkapi.messages.send(message=(phrases.pop() % showme.group(2)),
                                                user_id=parseitems[inte]['user_id'],
                                                attachment="photo" + str(attachment['owner_id']) + "_" + str(
                                                    attachment['id']))  # Отвечаем
                        elif bool(kurs):
                            jsondata = urllib.request.urlopen(
                                "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
                            decoded = json.loads(jsondata.readall().decode('utf-8'))
                            message = decoded[0]['ccy'] + " prodaut za " + decoded[0]['sale'] + ", a " + decoded[1][
                                'ccy'] + " prodaut za " + decoded[1]['sale']
                            vkapi.messages.setActivity(user_id=info['id'], type="typing")
                            time.sleep(2)
                            vkapi.messages.send(message=message, user_id=parseitems[inte]['user_id'])  # Отвечаем
                        elif bool(infa):
                            random.seed(infa.group(2))
                            percent = random.randint(0, 100)
                            message = infa.group(2) + " инфа " + str(percent) + "%"
                            vkapi.messages.send(message=message, user_id=parseitems[inte]['user_id'])  # Отвечаем
                        elif bool(iliili):
                            iliphrases = (["Ну... Наверное %s",
                                           "Вот честно тебе сказать, я думаю, что все-таки %s",
                                           "Конечно же %s", "%s - абсолютно без сомнений"])
                            ilipick = ([iliili.group(1), iliili.group(3)])
                            random.shuffle(ilipick)
                            random.shuffle(iliphrases)
                            message = iliphrases.pop() % ilipick.pop()
                            vkapi.messages.send(message=message, user_id=parseitems[inte]['user_id'])  # Отвечаем
                        else:
                            session = requests.post("http://bot.mew.su/service/getsession.php",
                                                    data={'id': str(info['id']), 'botid': bid}, verify=False)
                            print("=== Сообщение в ЛС =======")
                            # print(session.text)
                            resp = requests.post("http://bot.mew.su/service/speak.php",
                                                 data={'session': session.text, 'botid': str(jsn['id']),
                                                       'sender': str(info['id']), 'ischat': '0',
                                                       'text': parseitems[inte]['body'], 'version': version},
                                                 verify=False)
                            print(info['first_name'], info['last_name'], "-", info['id'])
                            print(parseitems[inte]['body'])
                            print("Ответ:", resp.text)
                            print("==========================")
                            vkapi.messages.setActivity(user_id=info['id'], type="typing")
                            time.sleep(2)
                            vkapi.messages.send(message=resp.text, user_id=parseitems[inte]['user_id'])  # Отвечаем
                else:
                    if parseitems[inte]['out'] == 0:

                        # ЭТА ЧАСТЬ ДЛЯ ЧАТА
                        namecheck = re.search(r'(' + firstname + '|лорочка|ларисонька|уеба)[\s|,|\.](.*)',
                                              parseitems[inte]['body'], re.IGNORECASE)
                        if namecheck:
                            showme = re.search(r'(покажи мне|как выглядит|покажи)\s(.*)', namecheck.group(2),
                                               re.IGNORECASE)
                            kurs = re.search(r'какой курс', namecheck.group(2), re.IGNORECASE)
                            infa = re.search(r'(сколько инфа|какая вероятность|какова вероятность)[ того]?\s(.*)',
                                             namecheck.group(2), re.IGNORECASE)
                            iliili = re.search(r'(.*)\s(или)(.*)?\?', namecheck.group(2), re.IGNORECASE)

                        mes = parseitems[inte]['chat_id']
                        # TODO: Ловить все запросы к доп. функциям
                        if bool(namecheck):
                            if bool(showme):
                                text = urllib.parse.quote(showme.group(2))
                                jsondata = urllib.request.urlopen(
                                    "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&userip="
                                    + socket.gethostname() +
                                    "&rsz=1&safe=off&imgsz=large&q="
                                    + text +
                                    "&start=0")
                                decoded = json.loads(jsondata.readall().decode('utf-8'))
                                dec = decoded['responseData']['results'].pop()
                                urllib.request.urlretrieve(dec['unescapedUrl'], "images/attach.jpg")
                                photoserver = vkapi.photos.getMessagesUploadServer()
                                photo = {'photo': ('images/attach.jpg', open('images/attach.jpg', 'rb'))}
                                r = requests.post(photoserver['upload_url'], files=photo, verify=False)
                                rjs = json.loads(r.text)
                                attachment = vkapi.photos.saveMessagesPhoto(photo=rjs['photo'], server=rjs['server'],
                                                                            hash=rjs['hash']).pop()
                                phrases = (["Я думаю это то, что ты искал по запросу %s",
                                            "Я на правильном пути? %s это картинка ниже?", "Это оно? %s?",
                                            "Я считаю что вот то, что тебе нужно. Запрос: %s", "%s - вот же"])
                                random.shuffle(phrases)
                                vkapi.messages.setActivity(chat_id=str(mes), type="typing")
                                time.sleep(2)
                                vkapi.messages.send(message=(phrases.pop() % showme.group(2)), chat_id=mes,
                                                    attachment="photo" + str(attachment['owner_id']) + "_" + str(
                                                        attachment['id']))  # Отвечаем
                            elif bool(kurs):
                                jsondata = urllib.request.urlopen(
                                    "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
                                decoded = json.loads(jsondata.readall().decode('utf-8'))
                                message = decoded[0]['ccy'] + " prodaut za " + decoded[0]['sale'] + ", a " + decoded[1][
                                    'ccy'] + " prodaut za " + decoded[1]['sale']
                                vkapi.messages.send(message=message, chat_id=mes)  # Отвечаем
                            elif bool(infa):
                                random.seed(infa.group(2))
                                percent = random.randint(0, 100)
                                message = infa.group(2), "инфа", str(percent), "%"
                                vkapi.messages.send(message=message, chat_id=mes)  # Отвечаем
                            elif bool(iliili):
                                iliphrases = (["Ну... Наверное %s",
                                               "Вот честно тебе сказать, я думаю, что все-таки %s",
                                               "Конечно же %s", "%s - абсолютно без сомнений"])
                                ilipick = ([iliili.group(1), iliili.group(3)])
                                random.shuffle(ilipick)
                                random.shuffle(iliphrases)
                                message = iliphrases.pop() % ilipick.pop()
                                vkapi.messages.send(message=message, chat_id=mes)  # Отвечаем

                            else:
                                session = requests.post("http://bot.mew.su/service/getsession.php",
                                                        data={'id': str(info['id']), 'botid': bid}, verify=False)
                                resp = requests.post("http://bot.mew.su/service/speak.php",
                                                     data={'session': session.text, 'botid': str(jsn['id']),
                                                           'sender': str(info['id']), 'ischat': '1',
                                                           'text': namecheck.group(2)}, verify=False)
                                print("==== Сообщение в ЧАТ =====")
                                print(info['first_name'], info['last_name'], "-", mes)
                                print(parseitems[inte]['body'])
                                print("Ответ:", resp.text)
                                print("==========================")
                                vkapi.messages.send(message=resp.text, chat_id=mes)  # Отвечаем
                time.sleep(1)
                inte += 1  # adding to loop

    except:
        printexception(jsn['id'])
        pass