from dbConnector import dbConnector
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from pyparsing import *
#from staszek import staszek
import logging
import sys
import os
from random import randint, choice, shuffle, seed, sample, uniform
from time import time, localtime, strftime
from threading import Thread
from texts import *
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

hpath=os.environ.get('STASZEKHOME')
lastseed=time()
chpiclimit=0
dices = Optional(Word(nums), default='1')+oneOf('k K d D')+Word(nums)+Optional(oneOf('- + * /')+Word(nums))
db = dbConnector.Instance()
mana = {}
STICKER, CATEGORY = range(2)
CHANNEL, CHSPECIAL, PHOTO = range(3)
QUESTION, ANSWER = range(2)

#answer functions:
def answerTxt(update, context, ans):
    ans='@'+findUserName(update, context)+': '+ans
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=ans)
def answerPicFromPath(update, context, path, caption):
    capt='@'+findUserName(update, context)+': '+caption
    context.bot.send_photo(chat_id=update.message.chat.id, photo=open(path, 'rb'), caption=capt)
def sendSticker(update,context,sid):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sid)
def sendLocation(update, context, loc):
    context.bot.send_location(chat_id=update.message.chat_id, latitude=loc['lat'], longitude=loc['long'])
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
    answerTxt(update, context, t['start'])
# main commands
def roll(update, context):
    try:
        s=context.args[0]
    except IndexError:
        rollSticker(update,context,'what')
        return True
    d=None
    for result in dices.scanString(s):
        d=result[0]
    rolldict=db.getRolls();
    if (not rolldict):
        answerTxt(update, context, t['error'])
        return True
    if (d):
        answerTxt(update,context,rollDices(d))
    elif s in rolldict.keys():
        func=rolldict[s]
        context.args=context.args[1:]
        eval(func)
    else: rollSticker(update,context,'what')
def randMember(update, context):
    chid=update.message.chat.id
    if int(chid)>0:
        answerTxt(update,context,t['nogroup'])
        return True
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
def rollLocation(update, context):
    a=db.getAreas()
    wa=[]
    if not a:
        answerTxt(update,context,t['error'])
        return True
    for loc in a:
        if loc[4]>1:
            for i in range(loc[4]-1):
                wa.append(loc)
    if len(wa)>0: a=a+wa
    area=choice(a)
    loc={
        "lat":round(uniform(area[0], area[1]), 6),
        "long":round(uniform(area[2], area[3]), 6)
    }
    sendLocation(update,context,loc)

def rollChannelPic(update, context):
    global mana
    addFriend(update, context)
    path='resources/test.png'
    chid=update.message.chat.id
    if(chid>0):
        answerTxt(update,context,t['notallowed'])
        return True
    chdir=hpath+str(chid)
    if(not os.path.isdir(chdir)):
        answerTxt(update,context,t['notallowed'])
        return True
    udir=chdir+'/'+str(update.message.from_user.id)
    if(os.path.isdir(udir)):
        answerPicFromPath(update,context,randomPicFromPath(udir),t['freeroll'])
    else:
        if not chid in mana: mana[chid]=0
        if (mana[chid]<time()):
            m=randint(1,3600)
            mana[chid]=time()+m
            newtime=localtime(mana[chid])
            answerPicFromPath(update,context,randomPicFromPath(chdir),t['countdown']+str(m)+'s ('+strftime("%H:%M:%S",newtime)+')')
        else:
            answerTxt(update,context,t['nomana'])
    return True
def question(update, context):
    try:
        q=context.args[0]
    except IndexError:
        answerTxt(update, context, t['dunno'])
        return True
    a=db.getRandomAnswer(context.args[0])
    if not a: a=t['dunno']
    answerTxt(update, context, a)

#ADM Functions
def printUpdate(update, context):
    print(str(update))
def addChannel(update, context):
    chname=update.message.chat['title']
    chid=update.message.chat['id']
    ret='OK'
    if(not db.insertChannel(chid, chname)):
        ret=t['error']
    else:
        chdir=hpath+str(chid)
        if(not os.path.isdir(chdir)):
            try:
                os.mkdir(chdir)
            except OSError:
                ret=t['error']
    answerTxt(update, context, ret)

# converastion handlers
def addSticker(update, context):
    answerTxt(update, context, t['addstickerst1'])
    return STICKER
def addRollSticker(update, context):
    try:
        a=context.args[0]
        s=context.args[1]
    except IndexError:
        answerTxt(update, context, t['addrollsterr'])
        return True
    comm="rollSticker(update,context,''%s'')"% (s)
    if db.addRollSticker(comm,a):
        answerTxt(update, context, t['addrollstok'])
    else:
        answerTxt(update, context, t['error'])
    return True
def stickerWait(update,context):
    user_data = context.user_data
    user_data['stickerid'] = update.message.sticker['file_id']
    answerTxt(update, context, t['addstickerst2'])
    return CATEGORY
def stickerCatWait(update,context):
    user_data = context.user_data
    if db.addSticker(user_data['stickerid'],update.message.text):
        answerTxt(update, context, t['addstickerst3'])
    else:
        answerTxt(update, context, t['error'])
    return ConversationHandler.END
def addchphoto(update,context):
    chlist=db.getFriendlyChannels(update.message.from_user.id)
    if not chlist:
        answerTxt(update, context, t['notfriend'])
        return ConversationHandler.END
    if len(chlist) == 1:
        user_data = context.user_data
        user_data['phchid']=chlist[0][0]
        spec=checkSpecialPhotos(chlist[0][0])
        if len(spec)>0:
            olist=[(t['chphall'],0)]
            for el in spec:
                cuser=context.bot.getChatMember(chlist[0][0], int(el))
                user=cuser.user
                olist.append((t['chphspec']+user.name,int(el)))
            buttons=[]
            for el in olist:
                buttons.append(InlineKeyboardButton(el[0], callback_data=el[1]))
            reply_markup=InlineKeyboardMarkup(buildMenu(buttons,n_cols=1))
            update.message.reply_text(text=t['specphoto'],reply_markup=reply_markup)
            return CHSPECIAL
        else:
            answerTxt(update, context, t['photowait'])
            return PHOTO
    else:
        buttons=[]
        for el in chlist:
            buttons.append(InlineKeyboardButton(el[1], callback_data=el[0]))
        reply_markup=InlineKeyboardMarkup(buildMenu(buttons,n_cols=1))
        update.message.reply_text(t['choosegroup'], reply_markup=reply_markup)
        return CHANNEL
def buildMenu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
def checkSpecialPhotos(chid):
    chdir=hpath+str(chid)
    subfolders = [ f.name for f in os.scandir(chdir) if f.is_dir() ]
    return subfolders
def chNameWait(update,context):
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    user_data['phchid']=query.data
    spec=checkSpecialPhotos(query.data)
    if len(spec)>0:
        olist=[(t['chphall'],0)]
        for el in spec:
            cuser=context.bot.getChatMember(query.data, int(el))
            user=cuser.user
            olist.append((t['chphspec']+user.name,int(el)))
        buttons=[]
        for el in olist:
            buttons.append(InlineKeyboardButton(el[0], callback_data=el[1]))
        reply_markup=InlineKeyboardMarkup(buildMenu(buttons,n_cols=1))
        query.edit_message_text(text=t['specphoto'],reply_markup=reply_markup)
        return CHSPECIAL
    else:
        query.edit_message_text(text=t['photowait'])
        return PHOTO
def chSpecWait(update,context):
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    user_data['specphoto']=query.data
    query.edit_message_text(text=t['photowait'])
    return PHOTO
def chPhotoWait(update,context):
    user_data = context.user_data
    file_id = update.message.photo[-1].file_id
    newFile = context.bot.getFile(file_id)
    if int(user_data['specphoto'])>0:
        fname=hpath+str(user_data['phchid'])+"/"+str(user_data['specphoto'])+"/"+str(int(time()))+'.jpg'
    else:
        fname=hpath+str(user_data['phchid'])+"/"+str(int(time()))+'.jpg'
    newFile.download(fname)
    context.bot.sendMessage(chat_id=update.message.chat_id, text=t['phadded'])
    return ConversationHandler.END
def addAnswer(update, context):
    try:
        s=context.args[0]
        user_data = context.user_data
        user_data['question']=s
        answerTxt(update, context, t['addanswer'])
        return ANSWER
    except IndexError:
        answerTxt(update, context, t['addquestion'])
        return QUESTION
def questionWait(update, context):
    user_data = context.user_data
    user_data['question']=update.message.text
    answerTxt(update, context, t['addanswer'])
    return ANSWER
def answerWait(update, context):
    user_data = context.user_data
    if db.addAnswer(user_data['question'],update.message.text):
        answerTxt(update, context, t['answerok'])
    else:
        answerTxt(update, context, t['error'])
    return ConversationHandler.END
def cancel(update,context):
    answerTxt(update, context, 'CANCELED')
    return ConversationHandler.END
def timeout(update,context):
    answerTxt(update, context, t['ctimeout'])
    return ConversationHandler.END
def help(update,context):
    chid=update.message.chat.id
    helpfile=hpath+str(chid)+'/help.html'
    if not os.path.isfile(helpfile):
        helpfile='./help.html'
    with open(helpfile, 'r',encoding="utf-8") as helpf:
        update.message.reply_text(helpf.read(),parse_mode='HTML')


    return True
def main():
    def stop_and_restart():
            updater.stop()
            print(sys.executable)
            os.execl(sys.executable, '"'+sys.executable+'"', *sys.argv)

    def restart(update, context):
            update.message.reply_text(t['restart'])
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

    dispatcher.add_handler(CommandHandler('r', restart, Filters.user(user_id=bowner)))
    dispatcher.add_handler(CommandHandler('u', printUpdate, Filters.user(user_id=bowner)))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('addchannel', addChannel, Filters.user(user_id=bowner)))
    dispatcher.add_handler(CommandHandler('addrollsticker', addRollSticker, Filters.user(user_id=bowner)))
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member,rmFriend))


    add_sticker_handler = ConversationHandler(
        entry_points=[CommandHandler('addsticker', addSticker,Filters.user(user_id=bowner))],
        states={
            STICKER: [MessageHandler(Filters.sticker, stickerWait)],
            CATEGORY: [MessageHandler(Filters.text,stickerCatWait)],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=20
    )
    dispatcher.add_handler(add_sticker_handler)

    add_answer_handler = ConversationHandler(
        entry_points=[CommandHandler('addanswer', addAnswer,Filters.user(user_id=bowner))],
        states={
            QUESTION: [MessageHandler(Filters.text, questionWait)],
            ANSWER: [MessageHandler(Filters.text, answerWait)],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=20
    )
    dispatcher.add_handler(add_answer_handler)

    add_chphoto_handler = ConversationHandler(
        entry_points=[CommandHandler('addpic', addchphoto)],
        states={
            CHANNEL: [CallbackQueryHandler(chNameWait)],
            CHSPECIAL: [CallbackQueryHandler(chSpecWait)],
            PHOTO: [MessageHandler(Filters.photo, chPhotoWait)],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=20
    )
    dispatcher.add_handler(add_chphoto_handler)

    #dispatcher.add_handler(MessageHandler(Filters.sticker,printUpdate))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
	main()
