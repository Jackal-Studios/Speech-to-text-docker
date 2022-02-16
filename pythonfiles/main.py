#!/usr/bin/env python3
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.utils.callback_data import CallbackData
from time import time
import pickle
import os.path
#import speech_recognition as sr
from google.cloud import speech
import io
import os

help_text="To use this bot you have to select a language via the \"/language\" command and send the audio message you need to transcribe"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./secrets/googleapi.json"

#to get the current working directory
# directory = os.getcwd()
#
# print(directory)
# print("new3")
import ctypes
try:
 is_admin = os.getuid() == 0
except AttributeError:
 is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

# print (is_admin)
# while(True):
#     pass
API_TOKEN = open('./secrets/api.txt','r+').readline().strip().replace("\n","")
#print(API_TOKEN)
ids=[[451248878,'eng']]
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# ids=[[451248878,'eng']]
if(os.path.isfile('./db/my_ids.pickle')):
    with open('./db/my_ids.pickle', 'rb') as data:
        ids = pickle.load(data)
        data.close()

else:
    with open('./db/my_ids.pickle','wb') as output:
        pickle.dump(ids,output)
        output.close()
# with open('test.pickle','wb') as output:
#          pickle.dump(ids,output)
#          output.close()

vote_cb = CallbackData('vote', 'action')
start_time=time()
temporary_folder_path="./ramdisk/"
filecount=0
forward_mode=False
client = speech.SpeechClient()
tempfilename="voicemsg.wav"
tempfilename2="voicemsg.ogg"


def removetempfile(path):
    return os.remove(path)

def onelistening(chosen_language):
    print("onelistening function reached")
    if(os.path.isfile(temporary_folder_path + tempfilename)):
        removetempfile(temporary_folder_path + tempfilename)
    os.system('ffmpeg -i '+temporary_folder_path+tempfilename2+' -ac 1 '+temporary_folder_path+tempfilename)


    with io.open(temporary_folder_path+tempfilename, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        #sample_rate_hertz=16000,
        language_code=chosen_language)
    response= client.long_running_recognize(config=config, audio=audio).result(timeout=100)
    #response = client.recognize(config, audio)
    #deleting voice file
    removetempfile(temporary_folder_path+tempfilename2)
    removetempfile(temporary_folder_path+tempfilename)
    print("about to return")
    print(response)
    for result in response.results:
        #sendMessage(data['message']['chat']['id'], result.alternatives[0].transcript)
        #print(replied_message_id)
        #return (str(result.alternatives[0].transcript))
        return (str(result.alternatives[0].transcript))

@dp.message_handler(content_types=['voice'])
async def handle_voice(message):
    global ids
    global forward_mode
    if ((message.chat.id == 451248878 or message.chat.id == 386764197) and forward_mode == True):
        for y in ids:
            try:
                await bot.forward_message(y[0], 451248878, message["message_id"])
            except:
                print("Error forwarding to: {}".format(y[0]))
    used = False
    lang = "en-US"
    msgid=0
    for n in ids:
        if (message.chat.id in n):
            lang = str(n[1])
            await message.reply("Your audio is being processed(" + str(n[1]) + ")")
            msgid=message.message_id+1
            used = True
            break
        else:
            used = False
    if (used == False):
        await message.reply("Your audio is being processed(en-US)\n(if you want to change the language use \"/language\")")
        msgid = message.message_id + 1

    downloaded=False
    try:
        await message.voice.download(temporary_folder_path+tempfilename2)   #change to .wav?
        downloaded=True
    except:
        print("error downloading")
        downloaded=False
        await message.reply("There was an error downloading your file")
    if(downloaded):
        #try:
        rectext=onelistening(chosen_language=lang)
        print("########################################")
        print(rectext)
        await bot.edit_message_text(text=rectext,chat_id=message.chat.id,message_id=msgid)
        #except:
        #    print("error editing")
        #    await message.reply("there was an error recognizing your voice message")

    #
    # await message.voice.download('voice22.oga')   #change to .wav?
    # await bot.edit_message_text(text=onelistening(lang),chat_id=message.chat.id,message_id=message.message_id+1)
    # os.remove('voice22.wav')
    #await message.photo[-1].download(temporary_folder_path + message.id+'.jpg')
    #await bot.send_message(message.chat.id, ocr(lang))




#FRANCE \U0001F1EB\U0001F1F7
def get_keyboard():
    return types.InlineKeyboardMarkup().row(
        types.InlineKeyboardButton('English \U0001F1EC\U0001F1E7', callback_data=vote_cb.new(action='en-US'))).row(
        types.InlineKeyboardButton('Українська \U0001F1FA\U0001F1E6', callback_data=vote_cb.new(action='uk-UA')),
        types.InlineKeyboardButton('Deutsch \U0001F1E9\U0001F1EA', callback_data=vote_cb.new(action='de-DE')),
        types.InlineKeyboardButton('中文语言 \U0001F1E8\U0001F1F3', callback_data=vote_cb.new(action='zh'))).row(
        types.InlineKeyboardButton('हिंदुस्तानी \U0001F1EE\U0001F1F3', callback_data=vote_cb.new(action='hi-IN')),
        types.InlineKeyboardButton('Español \U0001F1EA\U0001F1E6', callback_data=vote_cb.new(action='es-ES')),
        types.InlineKeyboardButton('عربى' + '\U0001F1E6\U0001F1EA', callback_data=vote_cb.new(action='ar-SA'))).row(
        types.InlineKeyboardButton('Русский \U0001F1F7\U0001F1FA', callback_data=vote_cb.new(action='ru-RU')),
        types.InlineKeyboardButton('Portugues \U0001F1F5\U0001F1F9', callback_data=vote_cb.new(action='pt-PT')),
        types.InlineKeyboardButton('Française \U0001F1F2\U0001F1EB', callback_data=vote_cb.new(action='fr-FR')),)

@dp.errors_handler()
async def errors_handler(dispatcher, update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging
    """
    from aiogram.utils.exceptions import Unauthorized, InvalidQueryID, TelegramAPIError, \
        CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound, BotBlocked
    if isinstance(exception, Exception):
        print("error ocured")
        return
    if isinstance(exception, BotBlocked):
        print("bot blocked")
        return
    if isinstance(exception, CantDemoteChatCreator):
        print("Can't demote chat creator")
        return

    if isinstance(exception, MessageNotModified):
        print('Message is not modified')
        return

    if isinstance(exception, MessageToDeleteNotFound):
        print('Message to delete not found')
        return

    if isinstance(exception, Unauthorized):
        print('Unauthorized: {}'.format(exception))
        return

    if isinstance(exception, InvalidQueryID):
        print('InvalidQueryID: {} \nUpdate: {}'.format(exception,update))
        return

    if isinstance(exception, TelegramAPIError):
        print('TelegramAPIError: {} \nUpdate: {}'.format(exception,update))
        return
    print('Update: {} \n{}'.format(update,exception))

@dp.message_handler(commands=['start', 'help'])
async def helpmessage(message: types.Message):
    print("started!")
    await bot.send_message(message.chat.id, help_text)

@dp.message_handler(commands=['language'])
async def languageselection(message: types.Message):
    await bot.send_message(message.chat.id,"Choose language",reply_markup=get_keyboard() )


@dp.callback_query_handler(vote_cb.filter(action=['en-US', 'uk-UA','de-DE','zh','hi-IN','es-ES','ar-SA','ru-RU','pt-PT','fr-FR']))
async def callback_vote_action(query: types.CallbackQuery, callback_data: dict):
    logging.info('Got this callback data: %r', callback_data)  # callback_data contains all info from callback data
    await query.answer()  # don't forget to answer callback query as soon as possible
    callback_data_action = callback_data['action']
    global ids
    used=False
    for n in ids:
        if(query.message.chat.id in n):
            ids[ids.index(n)]= [query.message.chat.id,callback_data_action]
            used=True
            break
        else:
            used=False
    if(used==False):
        ids.append([query.message.chat.id,callback_data_action])
    with open('./db/my_ids.pickle','wb') as output:
        pickle.dump(ids,output)


#Admin message handlers
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    global ids
    if(message.chat.id==451248878 or message.chat.id==386764197):
        unix_uptime=time()-start_time
        await message.reply("Total users:"+str(len(ids))+"\nFiles OCRed:"+str(filecount)+"\nUptime: "+str(int(unix_uptime/60/60/24))+         ####################
                            " days, "+str(int(unix_uptime/60/60)%60)+" hours, "+str(int(unix_uptime/60)%60)+" minutes")
@dp.message_handler(commands=['forward'])
async def forwardmode(message: types.Message):
    global forward_mode
    print(message.chat.id)
    if(message.chat.id==451248878 or message.chat.id==386764197):
        forward_mode=True
        await message.reply("WARNING, You entered the forwarding mode, to cancel write /cancel")
@dp.message_handler(commands=['cancel'])
async def cancelforwardmode(message: types.Message):
    global forward_mode
    if((message.chat.id==451248878 or message.chat.id==386764197)):
        forward_mode=False
        await message.reply("Exited forwarding mode")

#deal later
@dp.message_handler()
async def allmessageshandling(message: types.Message):
    global ids
    me= await bot.get_me()
    #print(me.username)
    try:
        global forward_mode
        if((message.chat.id==451248878 or message.chat.id==386764197) and forward_mode==True and message["text"]!="/cancel"):
            for i in ids:
                await bot.forward_message(i[0],451248878,message["message_id"])
    except:
        await message.reply("there was an error")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
