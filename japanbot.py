#Daniel Ponturo
#2018
#JapanBot



from googletrans import Translator
import telepot, time
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os
import speech_recognition as sr
import mysql.connector
import re
import datetime
from os import path
import subprocess

TOKEN = #insert token
translator = Translator()
db= mysql.connector.connect(host= , #insert MySQL DB host name
                            user= , #insert MySQL DB username
                            passwd= , #insert MySQL DB password
                            db= #insert MySQL DB name
                            )


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text' and msg['text'] == '/start':
      cur= db.cursor()
      cur.execute("SELECT chat_id FROM Users WHERE chat_id= %s", (str(chat_id),))
      q= str(cur.fetchall())
      cur.close()
      query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
      print("The query returned",query_t)
      user_info= list(msg['from'].values())[4]
      if query_t == "":
          cur= db.cursor()
          cur.execute("INSERT INTO Users(chat_id, username) VALUES (%s,%s)", (str(chat_id),str(user_info)))
          db.commit()
          print("New user added to the database",str(chat_id),str(user_info))
      bot.sendMessage(chat_id, "This bot can translate and pronounce things to and from Japanese. Use the command /help to get to know more about how the bot works. はじめましょうね :)")
    elif content_type == 'text' and str(msg['text'])[0:14] == '/pronunciation':
        print("Pronunciation service requested from "+str(chat_id))
        message= str(msg['text'])
        mp= message[15:len(message)]
        print("Message to pronounce: "+mp)
        if mp == '':
            print("Empty message, notifying the user")
            bot.sendMessage(chat_id, "Wrong syntax, use the /help command to know more about the usage of the pronunciation command")
        else:
            language= str(translator.detect(mp))
            if 'ja' or 'cn' in language:
                print("Language is JA")
                pronunciation= gTTS(text=mp, lang='ja')
                pronunciation.save("pronunciation.mp3")
                print("pronunciation.mp3 file has been saved")
                bot.sendAudio(chat_id, open('pronunciation.mp3', 'rb'), title='Pronunciation of '+mp)
                print("pronunciation.mp3 file has been sent to "+str(chat_id))
                os.remove("pronunciation.mp3")
                print("pronunciation.mp3 file has been removed")
                params= (str(chat_id),'pronunciation','ja',mp,str(msg['date']))
                cur= db.cursor()
                cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, timestamp_txt) VALUES (%s, %s, %s, %s, %s)", params)
                db.commit()
                print("Informations about the pronunciation have been added to the database")
            else:
                print("Language is not JA")
                bot.sendMessage(chat_id, "The message is not in Japanese. To have the bot pronunciating something, please send a message in Japanese")
    elif content_type == 'text' and str(msg['text'])[0:12] == '/translation':
        print("Translation service requested from "+str(chat_id))
        message= str(msg['text'])
        mp= message[13:len(message)]
        print("Message to translate: "+mp)
        if mp == '':
            print("Empty message, notifying the user")
            bot.sendMessage(chat_id, "Wrong syntax, use the /help command to know more about the usage of the translation command")
        else:
            language= str(translator.detect(mp))
            if 'ja' in language:
                print("Searching for a pre-existing translation for "+mp+" in the database...")
                cur= db.cursor()
                cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= 'ja' AND type= 'translation' AND contentbefore= %s", (mp,))
                q= str(cur.fetchall())
                cur.close()
                query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
                print("The query returned",query_t)
                if query_t == '':
                    print("Pre-existing translation not found, "+mp+" will be translated using the googletrans API")
                    translation= translator.translate(mp, dest='en')
                    print(translation.origin, ' -> ', translation.text)
                    bot.sendMessage(chat_id, translation.text)
                    print("The translation has been sent to "+str(chat_id))
                    params= (str(chat_id),'translation','ja',mp,translation.text,str(msg['date']))
                    cur= db.cursor()
                    cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                    db.commit()
                    print("Informations about the translation have been added to the database")
                else:
                    print("A pre-existing translation has been found")
                    bot.sendMessage(chat_id, query_t)
                    print("The translation has been sent to "+str(chat_id))
                    params= (str(chat_id),'translation','ja',mp,query_t,str(msg['date']))
                    cur= db.cursor()
                    cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                    db.commit()
                    print("Informations about the translation have been added to the database")

            else:
                lcode= language[14:16]
                print("Searching for a pre-existing translation for "+mp+" in the database...")
                cur= db.cursor()
                cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og=%s AND type= 'translation' AND contentbefore= %s", (lcode,mp))
                q= str(cur.fetchall())
                cur.close()
                print(q)
                query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
                print("The query returned",query_t)
                if query_t == '':
                    print("Pre-existing translation not found, "+mp+" will be translated using the googletrans API")
                    translation= translator.translate(mp, dest='ja')
                    print(translation.origin, ' -> ', translation.text)
                    bot.sendMessage(chat_id, translation.text)
                    print("The translation has been sent to "+str(chat_id))
                    params= (str(chat_id),'translation',lcode,mp,translation.text,str(msg['date']))
                    cur= db.cursor()
                    cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                    db.commit()
                    print("Informations about the translation have been added to the database")
                else:
                    print("A pre-existing translation has been found")
                    bot.sendMessage(chat_id, query_t)
                    print("The translation has been sent to "+str(chat_id))
                    lcode= language[14:16]
                    params= (str(chat_id),'translation',lcode,mp,query_t,str(msg['date']))
                    cur= db.cursor()
                    cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                    db.commit()
                    print("Information about the translation has been added to the database")
    elif content_type == 'text' and str(msg['text'])[0:8] == '/queries':
        markup = InlineKeyboardMarkup(inline_keyboard=[
             [dict(text='Total number of messages sent to the bot from the first startup to the moment the query has been executed', callback_data='n_total')],
             [InlineKeyboardButton(text='Date of the first message sent to the bot (/start, /help, /queries and /advanced messages are not counted)', callback_data='first')],
             [dict(text='Date of the last message sent to the bot (/start, /help, /queries and /advanced messages are not counted)', callback_data='last')],
             [InlineKeyboardButton(text='Total number of pronunciation requests sent to the bot from the first startup to the moment the query has been executed', callback_data='pronun')],
             [dict(text='Total number of translation requests sent to the bot from the first startup to the moment the query has been executed', callback_data='trans')],
             ])
        bot.sendMessage(chat_id, "Use the buttons to perform basic queries on the bot's database", reply_markup=markup)
    elif content_type == 'text' and str(msg['text'])[0:5] == '/help':
                markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Translation', callback_data='translation')],
                     [InlineKeyboardButton(text='Vocal translation', callback_data='voice')],
                     [InlineKeyboardButton(text='Pronunciation', callback_data='pronunciation')],
                     [dict(text='Queries', callback_data='queries')],
                     [InlineKeyboardButton(text='Switch to using bot inline', switch_inline_query='')],
                     ])
                bot.sendMessage(chat_id, 'Help section, use the buttons to get information on how the bot works', reply_markup=markup)
    elif content_type == 'voice':
        bot.download_file(msg['voice']['file_id'], './voice.ogg')
        command= subprocess.Popen(["ffmpeg","-i","voice.ogg","-ab", "128000", "voice.wav"], stdout=subprocess.PIPE)
        output= command.communicate()[0]
        r= sr.Recognizer()
        with sr.AudioFile("voice.wav") as source:
            audio= r.record(source)
        try:
            message= r.recognize_sphinx(audio)
            bot.sendMessage(chat_id,"The bot thinks you said '"+message+"'")
            print("Searching for a pre-existing translation for "+message+" in the database...")
            cur= db.cursor()
            cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= 'en' AND type= 'translation' AND contentbefore= %s OR language_og= 'en' AND type= 'v_translation' AND contentbefore= %s", (message,message))
            q= str(cur.fetchall())
            cur.close()
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
            print("The query returned",query_t)
            if query_t == '':
                print("Pre-existing translation not found, "+message+" will be translated using the googletrans API")
                translation= translator.translate(message, dest='ja')
                print(translation.origin, ' -> ', translation.text)
                bot.sendMessage(chat_id, translation.text)
                print("The translation has been sent to "+str(chat_id))
                params= (str(chat_id),'v_translation','en',message,translation.text,str(msg['date']))
                cur= db.cursor()
                cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                db.commit()
                print("Information about the translation has been added to the database")
            else:
                print("A pre-existing translation has been found")
                bot.sendMessage(chat_id, query_t)
                print("The translation has been sent to "+str(chat_id))
                params= (str(chat_id),'v_translation','en',message,query_t,str(msg['date']))
                cur= db.cursor()
                cur.execute("INSERT INTO Texts(chat_id, type, language_og, contentbefore, contentafter, timestamp_txt) VALUES (%s, %s, %s, %s, %s, %s)", params)
                db.commit()
                print("Information about the translation has been added to the database")
        except sr.UnknownValueError:
            print("Bot could not understand voice message")
            bot.sendMessage(chat_id,"The bot could not understand your voice message. Make sure to send only voice messages in English and to also make sure they are understandable")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            bot.sendMessage(chat_id,"An error occurred, please try later")

        os.remove("voice.ogg")
        os.remove("voice.wav")

def on_inline_query(msg):
    query_id, chat_id, query_string= telepot.glance(msg, flavor='inline_query')
    def compute():
        print ('Inline Query:', query_id, chat_id, query_string)
        string_nt= str(query_string)
        language= str(translator.detect(string_nt))
        if 'ja' in language:
            print("Searching for a pre-existing translation for "+string_nt+" in the database...")
            cur= db.cursor()
            cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= 'ja' AND type= 'translation' AND contentbefore= %s", (string_nt,))
            q= str(cur.fetchall())
            cur.close()
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
            print("The query returned",query_t)
            if query_t == '':
                print("Pre-existing translation not found, "+string_nt+" will be translated using the googletrans API")
                translation= translator.translate(string_nt, dest='en')
                print(translation.origin, ' -> ', translation.text)
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate from Japanese...',input_message_content=InputTextMessageContent(message_text=translation.text))]
            else:
                print("A pre-existing translation has been found")
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate from Japanese...',input_message_content=InputTextMessageContent(message_text=query_t))]
        else:
            lcode= language[14:16]
            print("Searching for a pre-existing translation for "+string_nt+" in the database...")
            cur= db.cursor()
            cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= %s AND type= 'translation' AND contentbefore= %s", (lcode,string_nt))
            q= str(cur.fetchall())
            cur.close()
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q))
            print("The query returned",query_t)
            if query_t == '':
                print("Pre-existing translation not found, "+string_nt+" will be translated using the googletrans API")
                translation= translator.translate(string_nt, dest='ja')
                print(translation.origin, ' -> ', translation.text)
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate to Japanese...',input_message_content=InputTextMessageContent(message_text=translation.text))]
            else:
                print("A pre-existing translation has been found")
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate to Japanese...',input_message_content=InputTextMessageContent(message_text=query_t))]
        return translatedstr
    a= answerer.answer(msg, compute)

def on_callback_query(msg):
    query_id, chat_id, query_data= telepot.glance(msg, flavor= 'callback_query')
    if query_data == 'translation':
        bot.sendMessage(chat_id, 'To have the bot translating text from any given language to Japanese or the other way round, please write /translation+space+the text you want to have translated. (ex: /translation test)')
        print("Help -> translation", query_id, chat_id)
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'voice':
        bot.sendMessage(chat_id, 'Simply send a voice message in English to have it translated to Japanese')
        print("Help -> voice translation", query_id, chat_id)
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'pronunciation':
        bot.sendMessage(chat_id, 'To have the bot pronunciating some Japanese text, please write /pronunciation+space+the Japanese text you want to have pronounced. (ex: /pronunciation テスト)')
        print("Help -> pronunciation", query_id, chat_id)
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'queries':
        bot.sendMessage(chat_id, 'To execute basic queries on the database of the bot, use the command /queries. You will receive a reply message with various buttons to perform queries')
        print("Help -> queries", query_id, chat_id)
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'n_total':
        print("Query -> total", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id=Users.chat_id", (chat_id,))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a))
        print("The query returned:",final_t)
        bot.sendMessage(chat_id, "The total number of messages sent by you to the bot since the first startup is "+str(final_t))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'pronun':
        print("Query -> pronunciations", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"pronunciation"))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a))
        print("The query returned:",final_t)
        bot.sendMessage(chat_id, "The total number of pronunciation requests sent by you to the bot since the first startup is "+str(final_t))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'trans':
        print("Query -> translations", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"translation"))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a))
        print("The first query returned:",final_t)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"v_translation"))
        voice_t= str(cur.fetchall())
        cur.close()
        v= re.findall('\d+', voice_t)
        final_v= re.sub("\[|\]|\'", '', str(v))
        print("The second query returned:",final_v)
        bot.sendMessage(chat_id, "The total number of translation requests sent by you to the bot since the first startup is "+str(final_t)+". You also sent "+str(final_v)+" voice message translation request/s")
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'last':
        print("Query -> last message to date", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT MAX(timestamp_txt) FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id= Users.chat_id", (chat_id,))
        last= str(cur.fetchall())
        cur.close()
        la= re.findall('\d+', last)
        l= re.sub("\[|\]|\'", '', str(la))
        final_l= datetime.datetime.fromtimestamp(int(l))
        print("The query returned",final_l)
        bot.sendMessage(chat_id,"The last message you sent to the bot is dated "+str(final_l))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
    elif query_data == 'first':
        print("Query -> first message to date", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT MIN(timestamp_txt) FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id= Users.chat_id", (chat_id,))
        first= str(cur.fetchall())
        cur.close()
        fa= re.findall('\d+', first)
        f= re.sub("\[|\]|\'", '', str(fa))
        final_f= datetime.datetime.fromtimestamp(int(f))
        print("The query returned",final_f)
        bot.sendMessage(chat_id,"The first message you sent to the bot is dated "+str(final_f))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')


bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)
bot.message_loop({'chat': on_chat_message,'inline_query': on_inline_query,'callback_query': on_callback_query},run_forever=True)
