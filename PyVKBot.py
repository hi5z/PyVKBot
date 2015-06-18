import vk, time, requests, re, json, urllib.parse, socket, random, linecache, sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

vkapi = vk.API(access_token='СЮДА НУЖНО ВСТАВИТЬ ACCESS_TOKEN')
jsn = vkapi.users.get().pop()

i = 0
while True: # Infinite loop
    try:
        if i == 0:
            # TODO: Проверка старых неотвеченых сообщений
            longpoll = vkapi.messages.getLongPollServer(need_pts=1,use_ssl=0)
            ts1 = longpoll['ts']
            pts1 = longpoll['pts']
            print("Принимаем сообщения...")
        else:
            longpoll = vkapi.messages.getLongPollServer(need_pts=1,use_ssl=0)
            ts1 = longpoll['ts']
            pts1 = newpts['new_pts']

        time.sleep(2)
        newpts = vkapi.messages.getLongPollHistory(pts=pts1,ts=ts1)

        #print(newpts)
        i = i + 1
        
        if not len(newpts['profiles']) == 0:
            info = newpts['profiles'].pop()
            history = newpts['messages']['items'].pop()

            print(history)
            if not 'chat_id' in history:

                if history['out'] == 0:

                    # ЭТА ЧАСТЬ ДЛЯ ПЕРСОНАЛЬНОГО ЧАТА
                    showme = re.search(r'(покажи[ мне]?|как выглядит)\s(.*)', history['body'], re.IGNORECASE)
                    kurs = re.search(r'курс', history['body'], re.IGNORECASE)
                    infa = re.search(r'(сколько инфа)\s(.*)', history['body'], re.IGNORECASE)

                    if bool(showme) == True:
                        text = urllib.parse.quote(showme.group(2))
                        jsondata = urllib.request.urlopen("http://ajax.googleapis.com/ajax/services/search/images?v=1.0&userip=" + socket.gethostname() + "&rsz=1&safe=off&imgsz=large&q=" + text + "&start=0")
                        decoded = json.loads(jsondata.readall().decode('utf-8'))
                        dec = decoded['responseData']['results'].pop()
                        urllib.request.urlretrieve(dec['unescapedUrl'], "images/attach.jpg")
                        photoserver = vkapi.photos.getMessagesUploadServer()
                        photo = {'photo': ('images/attach.jpg', open('images/attach.jpg', 'rb'))}
                        r = requests.post(photoserver['upload_url'], files = photo )
                        rjs = json.loads(r.text)
                        attachment = vkapi.photos.saveMessagesPhoto(photo=rjs['photo'], server=rjs['server'], hash=rjs['hash']).pop()
                        phrases = (["Я думаю это то, что ты искал по запросу %s", "Я на правильном пути? %s это картинка ниже?", "Это оно? %s?", "Я считаю что вот то, что тебе нужно. Запрос: %s", "%s - вот же"])
                        random.shuffle(phrases)
                        #print (attachment)
                        #print ("kool", dec['url'])

                        vkapi.messages.markAsRead(peer_id=info['id']); vkapi.messages.setActivity(user_id=info['id'], type="typing"); time.sleep(2);
                        vkapi.messages.send(message=(phrases.pop() % showme.group(2)), user_id=info['id'], attachment="photo"+str(attachment['owner_id'])+"_"+str(attachment['id'])) #Отвечаем
                    elif bool(kurs) == True:
                        jsondata = urllib.request.urlopen("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
                        decoded = json.loads(jsondata.readall().decode('utf-8'))
                        #print ("kursa zahotel? AHAHAHAHAHAHA", decoded[0]['sale'])
                        message = decoded[0]['ccy'] + " prodaut za " + decoded[0]['sale'] + ", a "+ decoded[1]['ccy'] + " prodaut za " + decoded[1]['sale']
                        vkapi.messages.markAsRead(peer_id=info['id']); vkapi.messages.setActivity(user_id=info['id'], type="typing"); time.sleep(2);
                        vkapi.messages.send(message=message, user_id=info['id']) #Отвечаем
                    elif bool(infa) == True:
                            random.seed(infa.group(2))
                            percent = random.randint(0,100)
                            message = infa.group(2) + " инфа " + str(percent) + "%"
                            vkapi.messages.send(message=message, user_id=info['id']) #Отвечаем
                    else:
                        session = requests.get("http://bot.mew.su/service/getsession.php?id="+str(info['id']))
                        print("=== Сообщение в ЛС =======")
                        #print(session.text)
                        resp = requests.get("http://bot.mew.su/service/speak.php?&session="+session.text+"&botid="+str(jsn['id'])+"&sender="+str(info['id'])+"&ischat=0&text="+history['body'])
                        print(info['first_name'], info['last_name'], "-",info['id'])
                        print(history['body'])
                        print("Ответ:", resp.text)
                        print("==========================")



                        vkapi.messages.markAsRead(peer_id=info['id']); vkapi.messages.setActivity(user_id=info['id'], type="typing"); time.sleep(2);
                        vkapi.messages.send(message=resp.text, user_id=info['id']) #Отвечаем
            else:
                if history['out'] == 0:

                    # ЭТА ЧАСТЬ ДЛЯ ЧАТА
                    namecheck = re.search(r'(лариса|лорочка|ларисонька|уеба)[\s|\,|\.](.*)', history['body'], re.IGNORECASE)
                    if namecheck:
                        showme = re.search(r'(покажи мне|как выглядит|покажи)\s(.*)', namecheck.group(2), re.IGNORECASE)
                        kurs = re.search(r'какой курс', namecheck.group(2), re.IGNORECASE)
                        infa = re.search(r'(сколько инфа)\s(.*)', namecheck.group(2), re.IGNORECASE)

                    mes = history['chat_id']

                    if bool(namecheck) == True:
                        if bool(showme) == True:
                            text = urllib.parse.quote(showme.group(2))
                            jsondata = urllib.request.urlopen("http://ajax.googleapis.com/ajax/services/search/images?v=1.0&userip=" + socket.gethostname() + "&rsz=1&safe=off&imgsz=large&q=" + text + "&start=0")
                            decoded = json.loads(jsondata.readall().decode('utf-8'))
                            dec = decoded['responseData']['results'].pop()
                            urllib.request.urlretrieve(dec['unescapedUrl'], "images/attach.jpg")
                            photoserver = vkapi.photos.getMessagesUploadServer()
                            photo = {'photo': ('images/attach.jpg', open('images/attach.jpg', 'rb'))}
                            r = requests.post(photoserver['upload_url'], files=photo)
                            rjs = json.loads(r.text)
                            attachment = vkapi.photos.saveMessagesPhoto(photo=rjs['photo'], server=rjs['server'], hash=rjs['hash']).pop()
                            phrases = (["Я думаю это то, что ты искал по запросу %s", "Я на правильном пути? %s это картинка ниже?", "Это оно? %s?", "Я считаю что вот то, что тебе нужно. Запрос: %s", "%s - вот же"])
                            random.shuffle(phrases)
                            vkapi.messages.send(message=(phrases.pop() % showme.group(2)), chat_id=mes, attachment="photo"+str(attachment['owner_id'])+"_"+str(attachment['id'])) #Отвечаем
                        elif bool(kurs) == True:
                            jsondata = urllib.request.urlopen("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5")
                            decoded = json.loads(jsondata.readall().decode('utf-8'))
                            message = decoded[0]['ccy'] + " prodaut za " + decoded[0]['sale'] + ", a "+ decoded[1]['ccy'] + " prodaut za " + decoded[1]['sale']
                            vkapi.messages.send(message=message, chat_id=mes) #Отвечаем
                        elif bool(infa) == True:
                            random.seed(infa.group(2))
                            percent = random.randint(0,100)
                            message = infa.group(2) + " инфа " + str(percent) + "%"
                            vkapi.messages.send(message=message, chat_id=mes) #Отвечаем

                        else:
                            session = requests.get("http://bot.mew.su/service/getsession.php?id="+str(info['id']))
                            resp = requests.get("http://bot.mew.su/service/speak.php?&session="+session.text+"&botid="+str(jsn['id'])+"&sender="+str(info['id'])+"&ischat=1&text="+namecheck.group(2))
                            print("==== Сообщение в ЧАТ =====")
                            print(info['first_name'], info['last_name'], "-",mes)
                            print(history['body'])
                            print("Ответ:", resp.text)
                            print("==========================")
                            vkapi.messages.send(message=resp.text, chat_id=mes) #Отвечаем



    except: # Пишем и пропускаем все exception'ы
        PrintException()
        pass