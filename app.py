from dbConnector import dbConnector
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import Filters
from pyparsing import *
#from staszek import staszek
import logging
import sys
import os
from random import randint, choice, shuffle, seed, sample
from time import time, localtime, strftime
from threading import Thread
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

hpath=os.environ.get('STASZEKHOME')
lastseed=time()
chpiclimit=0
dices = Optional(Word(nums), default='1')+oneOf('k K d D')+Word(nums)+Optional(oneOf('- + * /')+Word(nums))
db = dbConnector.Instance()
mana = {}


#answer functions:
def answerTxt(update, context, ans):
    ans='@'+findUserName(update, context)+': '+ans
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=ans)
def answerPicFromPath(update, context, path, caption):
    capt='@'+findUserName(update, context)+': '+caption
    context.bot.send_photo(chat_id=update.message.chat.id, photo=open(path, 'rb'), caption=capt)
def sendSticker(update,context,sid):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sid)

#usefull functions
def findUserName(update, context):
    tusername=update.message.from_user.first_name
    if (update.message.from_user.last_name): tusername=update.message.from_user.last_name
    if (update.message.from_user.username): tusername=update.message.from_user.username
    return tusername
def addFriend(update,context):
    user=update.message.from_user.id
    chid=update.message.chat.id
    db.insertFriend(user,chid)
def rmFriend(update,context):
    user=update.message.from_user.id
    chid=update.message.chat.id
    db.removeFriend(user,chid)
def listImgR(p):
    valid_images = [".jpg",".gif",".png"]
    list=[]
    for f in os.listdir(p):
        nd=str(p)+'/'+str(f)
        if os.path.isdir(nd):
            list=list+listImgR(nd)
        else:
            ext = os.path.splitext(f)[1]
            if ext.lower() not in valid_images:
                continue
            list.append(p+'/'+f)
    return list

def listImg(p):
    valid_images = [".jpg",".gif",".png"]
    list=[]
    for f in os.listdir(p):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        list.append(p+'/'+f)
    return list

#random things
def rseed():
    global lastseed
    if time()-lastseed>3600:
        seed(time())
        lastseed=time()
    return True
def randomPicFromPath(d):
    rseed()
    img=choice(listImg(d))
    return img
def rollDice(itype,reroll):
    tmp_ret=[]
    roll=randint(1,itype)
    tmp_ret.append(roll)
    if (reroll==1 and roll==itype):
        tmp_ret.extend(rollDice(itype,1))
    return tmp_ret




def rollDices(d):
    try:
        mod=d[3]+d[4]
    except IndexError:
        mod=''
    if int(d[0])>100: d[0]='100'
    if int(d[2])>1024: d[2]='1024'
    if d[1]=='D' or d[1]=='K':
        reroll=1
        if int(d[2])==1: reroll=0
    else: reroll=0
    dtab=[]
    for each in range(int(d[0])):
        dtab.extend(rollDice(int(d[2]),reroll))
    dtab.sort()
    rresult='('
    for el in dtab:
        rresult+=str(el)+'+'
    rresult=rresult[:-1]+')'+mod
    sum=eval(rresult)
    rresult=rresult+'='+str(sum)
    return rresult


def start(update, context):
    answerTxt(update, context, 'Jestem Bot. Staszek Bot.')
    #@#TODO Komunikat startowy niech bierze też z bazy jako parametr
# main commands
def roll(update, context):
    try:
        s=context.args[0]
    except IndexError:
        answerTxt(update, context, '?') #@#TODO tekst z bazy tekstów
        return True
    d=None
    for result in dices.scanString(s):
        d=result[0]
    rolldict=db.getRolls();
    if (not rolldict):
        answerTxt(update, context, 'stało się coś bardzo złego!')
        return True
    if (d):
        answerTxt(update,context,rollDices(d))
    elif s in rolldict.keys():
        func=rolldict[s]
        context.args=context.args[1:]
        eval(func)
    else: answerTxt(update,context,'Whaaat?')
def randMember(update, context):
    chid=update.message.chat.id
    if int(chid)>0:
        answerTxt(update,context,'We are alone here...')
        return true
    uid=db.getRandomFriend(str(chid))
    cuser=context.bot.getChatMember(chid, uid)
    user=cuser.user
    answerTxt(update,context,user.name)
def rollSticker(update,context,tag):
    sid=db.getRandomSticker(tag)
    sendSticker(update,context,sid)
def rollPic(update, context):
    path='resources/test.png'
    answerPicFromPath(update,context,path,'test')

def rollChannelPic(update, context):
    global mana
    addFriend(update, context)
    path='resources/test.png'
    chid=update.message.chat.id
    if(chid>0):
        answerTxt(update,context,'Yeah... nice try')
        return True
    chdir=hpath+str(chid)
    if(not os.path.isdir(chdir)):
        answerTxt(update,context,'Yeah... nice try')
        return True
    udir=chdir+'/'+str(update.message.from_user.id)
    if(os.path.isdir(udir)):
        answerPicFromPath(update,context,randomPicFromPath(udir),'no mana needed')
    else:
        if not chid in mana: mana[chid]=0
        if (mana[chid]<time()):
            m=randint(1,3600)
            mana[chid]=time()+m
            answerPicFromPath(update,context,randomPicFromPath(chdir),'Countdown:'+str(m))
        else:
            answerTxt(update,context,'Nie mam wystarczająco many')
    return True

def question(update, context):
    try:
        q=context.args[0]
    except IndexError:
        answerTxt(update, context, '?') #@#TODO tekst z bazy tekstów
        return True
    a=db.getRandomAnswer(context.args[0])
    if not a: a='nie wiem :(' #@#TODO tekst z bazy
    answerTxt(update, context, a)

#ADM Functions
def printUpdate(update, context):
    print(str(update))

def addChannel(update, context):
    chname=update.message.chat['title']
    chid=update.message.chat['id']
    ret='OK'
    if(not db.insertChannel(chid, chname)):
        ret='Operation failed'
    else:
        chdir=hpath+str(chid)
        if(not os.path.isdir(chdir)):
            try:
                os.mkdir(chdir)
            except OSError:
                ret='Cannot create directory for photos'
    answerTxt(update, context, ret)


def main():
    def stop_and_restart():
            updater.stop()
            print(sys.executable)
            os.execl(sys.executable, '"'+sys.executable+'"', *sys.argv)

    def restart(update, context):
            update.message.reply_text('Bot is restarting...')
            Thread(target=stop_and_restart).start()

#BOT Creation
    btoken=db.getParam('token')
    try:
        bowner=int(db.getParam('owner'))
    except ValueError:
        bowner=1

    if btoken==False:
        logging.error('No token! Did you configured this app correctly?')
        sys.exit(1)
    updater = Updater(token=btoken, use_context=True)
    dispatcher = updater.dispatcher



    comlist=db.getCommands()
    for com in comlist:
        if com[2]==1:
            dispatcher.add_handler(CommandHandler(com[0], eval(com[1])))
        if com[2]==2:
            c=com[1].split(" ")
            strf="""def %s(update, context):
                context.args=%s+context.args
                %s(update, context)
                """ % (com[0],c[1:],c[0])
            exec(strf)
            dispatcher.add_handler(CommandHandler(com[0], eval(com[0])))

    dispatcher.add_handler(CommandHandler('r', restart, Filters.user(user_id=bowner))) #@#TODO filtr na usera
    dispatcher.add_handler(CommandHandler('u', printUpdate, Filters.user(user_id=bowner)))
    dispatcher.add_handler(CommandHandler('addchannel', addChannel, Filters.user(user_id=bowner)))
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member,rmFriend))
    #dispatcher.add_handler(MessageHandler(Filters.sticker,printUpdate))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
	main()
