# japanbot
Telegram bot that translates from/to Japanese, written in Python (using the Telepot framework) as a high school final year project
(2017-2018 academic year).  
# What does japanbot do?
The project is a showcase of various skills learned both in an academic context and on my own. The aim of the bot is to provide an 
easy and reliable way of translating text (both in PM and inline modes) and voice messages on Telegram, by making use of the Google
Translate API and CMU Sphinx speech recognition software (through SpeechRecognition library), as well as being able to pronounce
Japanese text thanks to gTTS, Google Text to Speech API implementation in Python. Given that the project was used during the final
year exam setting, and also given that one of the skills learned during the 2017-2018 academic year was how to create and query
MySQL databases, the bot interfaces itself with a DB, saving information on the user and the operations requested, querying the 
database for previously requested operations (for example, not having to translate again a sentence or word already stored) and 
giving the user the possibility to execute basic queries via Telegram. 
# Additional info
The code is designed to be run on a Linux machine as a command-line, server side application to handle message exchanges 
between the user and the bot, as well as computing the various translations/pronunciations, storing and converting (through the
use of ffmpeg) the voice messages being sent by the user and printing in real time a log of the operations being executed.
