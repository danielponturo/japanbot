# Daniel Ponturo
# 2018
# JapanBot
# Telegram bot that translates from/to Japanese, written in Python 
# (using the telepot framework) as a high school final year project.
# Server-side code to be used on a Linux distribution. 
# Needs ffmpeg command line software to properly make use of the speech 
# recognition functionality.

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

TOKEN = #insert Telegram token
translator = Translator()
db= mysql.connector.connect(host= , #insert MySQL DB host name
                            user= , #insert MySQL DB username
                            passwd= , #insert MySQL DB password
                            db= #insert MySQL DB name
                            )




# Handles everything that happens when the bot receives a message from a user
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)


    # Everything that will be executed when the bot receives the command "/start"
    if content_type == 'text' and msg['text'] == '/start':
      cur= db.cursor()
      cur.execute("SELECT chat_id FROM Users WHERE chat_id= %s", (str(chat_id),)) # Interrogates the DB to find the ID of the user who sent the command "/start"
      q= str(cur.fetchall())
      cur.close()
      query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult 
      print("The query returned",query_t)
      user_info= list(msg['from'].values())[4] # Stores user info in a list format 
      
      if query_t == "": # An empty query result means that the user's info is not in the DB
          cur= db.cursor()
          cur.execute("INSERT INTO Users(chat_id, username) VALUES (%s,%s)", (str(chat_id),str(user_info)))
          db.commit()
          print("New user added to the database",str(chat_id),str(user_info))
          
      bot.sendMessage(chat_id, "This bot can translate and pronounce things to and from Japanese. Use the command /help to get to know more about how the bot works. はじめましょうね :)")


    # Everything that will be executed when the bot receives the command "/pronunciation + string to pronounce"   
    elif content_type == 'text' and str(msg['text'])[0:14] == '/pronunciation':
        print("Pronunciation service requested from "+str(chat_id))
        message= str(msg['text'])
        mp= message[15:len(message)] # Subs every character after the command "/pronunciation"
        print("Message to pronounce: "+mp)
        
        if mp == '':
            print("Empty message, notifying the user")
            bot.sendMessage(chat_id, "Wrong syntax, use the /help command to know more about the usage of the pronunciation command")

        else:
            language= str(translator.detect(mp)) # Makes use of the translator object to detect the language of the message to pronounce

            if 'ja' or 'cn' in language: 
                print("Language is JA")
                # A temp mp3 file with the pronunciation request is created, sent to the user and eliminated
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

                
    # Everything that will be executed when the bot receives the command "/translation + string to translate"               
    elif content_type == 'text' and str(msg['text'])[0:12] == '/translation':
        print("Translation service requested from "+str(chat_id))
        message= str(msg['text'])
        mp= message[13:len(message)] # Subs every character after the command "/translation"
        print("Message to translate: "+mp)
        
        if mp == '':
            print("Empty message, notifying the user")
            bot.sendMessage(chat_id, "Wrong syntax, use the /help command to know more about the usage of the translation command")
            
        else:
            language= str(translator.detect(mp))
            
            if 'ja' in language: # Translation from Japanese to English
                print("Searching for a pre-existing translation for "+mp+" in the database...")
                cur= db.cursor()
                cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= 'ja' AND type= 'translation' AND contentbefore= %s", (mp,))
                q= str(cur.fetchall())
                cur.close()
                query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult
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

            else: # Translation from the language of the text to Japanese
                lcode= language[14:16]
                print("Searching for a pre-existing translation for "+mp+" in the database...")
                cur= db.cursor()
                cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og=%s AND type= 'translation' AND contentbefore= %s", (lcode,mp))
                q= str(cur.fetchall())
                cur.close()
                print(q)
                query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult
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


    # Everything that will be executed when the bot receives the command "/queries"                
    elif content_type == 'text' and str(msg['text'])[0:8] == '/queries':
        # Creation of the Telegram inline keyboard which will be sent to the user to query the bot's database 
        markup = InlineKeyboardMarkup(inline_keyboard=[
             [dict(text='Total number of messages sent to the bot from the first startup to the moment the query has been executed', callback_data='n_total')],
             [InlineKeyboardButton(text='Date of the first message sent to the bot (/start, /help, /queries and /advanced messages are not counted)', callback_data='first')],
             [dict(text='Date of the last message sent to the bot (/start, /help, /queries and /advanced messages are not counted)', callback_data='last')],
             [InlineKeyboardButton(text='Total number of pronunciation requests sent to the bot from the first startup to the moment the query has been executed', callback_data='pronun')],
             [dict(text='Total number of translation requests sent to the bot from the first startup to the moment the query has been executed', callback_data='trans')],
             ])
        bot.sendMessage(chat_id, "Use the buttons to perform basic queries on the bot's database", reply_markup=markup)


    # Everything that will be executed when the bot receives the command "/help"    
    elif content_type == 'text' and str(msg['text'])[0:5] == '/help':
        # Creation of the Telegram inline keyboard which will be sent to the user to find more info on the bot
        markup = InlineKeyboardMarkup(inline_keyboard=[
             [dict(text='Translation', callback_data='translation')],
             [InlineKeyboardButton(text='Vocal translation', callback_data='voice')],
             [InlineKeyboardButton(text='Pronunciation', callback_data='pronunciation')],
             [dict(text='Queries', callback_data='queries')],
             [InlineKeyboardButton(text='Switch to using bot inline', switch_inline_query='')],
             ])
        bot.sendMessage(chat_id, 'Help section, use the buttons to get information on how the bot works', reply_markup=markup)


    # Everything that will be executed when the bot receives a voice message (translation of the voice note to Japanese)            
    elif content_type == 'voice':
        bot.download_file(msg['voice']['file_id'], './voice.ogg') # Saves the voice message as a .ogg audio file
        # The two following lines create a Linux command-line to convert voice.ogg to a .wav file using the program ffmpeg, to be used by the Speech Recognition utility, and execute it 
        command= subprocess.Popen(["ffmpeg","-i","voice.ogg","-ab", "128000", "voice.wav"], stdout=subprocess.PIPE) 
        output= command.communicate()[0]
        r= sr.Recognizer() # Instantiates speech recogniser object
        
        with sr.AudioFile("voice.wav") as source:
            audio= r.record(source)
            
        try:
            message= r.recognize_sphinx(audio) # What is said in the voice message is recognised using CMU Sphinx
            bot.sendMessage(chat_id,"The bot thinks you said '"+message+"'")
            print("Searching for a pre-existing translation for "+message+" in the database...")
            cur= db.cursor()
            cur.execute("SELECT DISTINCT contentafter FROM Texts WHERE language_og= 'en' AND type= 'translation' AND contentbefore= %s OR language_og= 'en' AND type= 'v_translation' AND contentbefore= %s", (message,message))
            q= str(cur.fetchall())
            cur.close()
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult
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




# Handles everything that happens when the bot is called inline (in a different Telegram chat from the bot's one)
def on_inline_query(msg):
    query_id, chat_id, query_string= telepot.glance(msg, flavor='inline_query')

    # Computes inline translations to/from Japanese
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
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult
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
            query_t= re.sub("\[|\]|\'|\(|\)|\,", '', str(q)) # Removes from the resulting string any character that might make its use inside the function difficult
            print("The query returned",query_t)
            
            if query_t == '':
                print("Pre-existing translation not found, "+string_nt+" will be translated using the googletrans API")
                translation= translator.translate(string_nt, dest='ja')
                print(translation.origin, ' -> ', translation.text)
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate to Japanese...',input_message_content=InputTextMessageContent(message_text=translation.text))]

            else:
                print("A pre-existing translation has been found")
                translatedstr= [InlineQueryResultArticle(id='inlinetranslate',title='Translate to Japanese...',input_message_content=InputTextMessageContent(message_text=query_t))]
                
        return translatedstr # Returns inline query result article computed beforehand
    
    a= answerer.answer(msg, compute)




# Handles replying to callback queries, generated when pressing a button on the inline keyboard for the commands "/queries" and "/help"
def on_callback_query(msg):
    query_id, chat_id, query_data= telepot.glance(msg, flavor= 'callback_query')

    # "/help" keyboard elements (info on the bot's functionalities)
    
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
        
    # "/queries" keyboard elements (queries on the bot's database for some of the user's data)  
     
    elif query_data == 'n_total': # Total number of messages sent by the user to the bot
        print("Query -> total", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id=Users.chat_id", (chat_id,))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a)) # Removes from the resulting string any character that might make its use inside the function difficult
        print("The query returned:",final_t)
        bot.sendMessage(chat_id, "The total number of messages sent by you to the bot since the first startup is "+str(final_t))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
        
    elif query_data == 'pronun': # Total number of pronunciation requests sent by the user to the bot
        print("Query -> pronunciations", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"pronunciation"))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a)) # Removes from the resulting string any character that might make its use inside the function difficult
        print("The query returned:",final_t)
        bot.sendMessage(chat_id, "The total number of pronunciation requests sent by you to the bot since the first startup is "+str(final_t))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
        
    elif query_data == 'trans': # Total number of translation requests sent by the user to the bot
        print("Query -> translations", query_id, chat_id)

        # Queries the DB for text translations
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"translation"))
        total= str(cur.fetchall())
        cur.close()
        a= re.findall('\d+', total )
        final_t= re.sub("\[|\]|\'", '', str(a)) # Removes from the resulting string any character that might make its use inside the function difficult
        print("The first query returned:",final_t)

        # Queries the DB for voice translations
        cur= db.cursor()
        cur.execute("SELECT COUNT(*) AS TOTAL FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.type= %s AND Texts.chat_id=Users.chat_id", (chat_id,"v_translation"))
        voice_t= str(cur.fetchall())
        cur.close()
        v= re.findall('\d+', voice_t)
        final_v= re.sub("\[|\]|\'", '', str(v)) # Removes from the resulting string any character that might make its use inside the function difficult
        print("The second query returned:",final_v)

        bot.sendMessage(chat_id, "The total number of translation requests sent by you to the bot since the first startup is "+str(final_t)+". You also sent "+str(final_v)+" voice message translation request/s")
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
        
    elif query_data == 'last': # Last message sent to the bot by the user to date
        print("Query -> last message to date", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT MAX(timestamp_txt) FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id= Users.chat_id", (chat_id,))
        last= str(cur.fetchall())
        cur.close()
        la= re.findall('\d+', last)
        l= re.sub("\[|\]|\'", '', str(la)) # Removes from the resulting string any character that might make its use inside the function difficult
        final_l= datetime.datetime.fromtimestamp(int(l)) # Converts the date of the last message from Linux timestamp format to a human-readable format
        print("The query returned",final_l)
        bot.sendMessage(chat_id,"The last message you sent to the bot is dated "+str(final_l))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')
        
    elif query_data == 'first': # First message sent to the bot by the user to date
        print("Query -> first message to date", query_id, chat_id)
        cur= db.cursor()
        cur.execute("SELECT MIN(timestamp_txt) FROM Texts,Users WHERE Texts.chat_id= %s AND Texts.chat_id= Users.chat_id", (chat_id,))
        first= str(cur.fetchall())
        cur.close()
        fa= re.findall('\d+', first)
        f= re.sub("\[|\]|\'", '', str(fa)) # Removes from the resulting string any character that might make its use inside the function difficult
        final_f= datetime.datetime.fromtimestamp(int(f)) # Converts the date of the first message from Linux timestamp format to a human-readable format
        print("The query returned",final_f)
        bot.sendMessage(chat_id,"The first message you sent to the bot is dated "+str(final_f))
        print("Sent message containing the query result to the user")
        bot.answerCallbackQuery(query_id, text='')




# Telepot operations
bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)
bot.message_loop({'chat': on_chat_message,'inline_query': on_inline_query,'callback_query': on_callback_query},run_forever=True)
