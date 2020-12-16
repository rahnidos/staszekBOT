# staszekBOT

## Telegram BOT made in Python

Staszek is a Telegram BOT build in Python, based on Python-Telegram-Bot.
Staszek was build for a friends Telegram Group, so if you do not have any friends this software might seems not to be usefull for you. But it isn't. Staszek can do a lot of things and now nearly everything. Just try.

It is still under development in beta testing phase.

## Requirements
Python 3
with modules installed:
- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [PyParsing](https://github.com/pyparsing/pyparsing)

## Installation

- Download and unzip last version of software from this repository.
- Create a directory for bot files - I'll call it bot home from now.
- Set environment variable: STASZEKHOME=_bot home path_
- Copy _staszek.db_ from repository to bot home directory
- Edit database with your favourite tool:
```sql
update settings set value=YOUR_TELEGRAM_USER_ID where key='owner';
update settings set value=BOT_TOKEN where key='token';
update settings set value=BOT_HOME_PAT where key='rpath';
```
- start bot with command: python3 app.py

###Set service in linux

Create service file:
```bash
sudo vi /lib/systemd/system/sbot.service
```
File content:
```bash
[Unit]
Description=StaszekBOT

[Service]
Type=simple
Environment=STASZEKHOME=_PATH_TO_BOT_HOME_
WorkingDirectory=_PATH_TO_DIRECTORY_WITH_SOFTWARE_
ExecStart=/usr/bin/python3 _PATH_TO_DIRECTORY_WITH_SOFTWARE_/app.py

[Install]
WantedBy=multi-user.target
```
Then reload deamon, enable and start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable sbot.service
sudo.systemctl start sbot.service
```

## Available commands
All commands are defined in db table commands. There are two types of them - real commands and aliases.
Real command must gave a callable bot function defined. Here is the list of callable functions:
- start - nothing special
- question [param] - answer random text from db table answers - based on parameter
- roll - function for doing random things - more information in Things to 'roll' section.
- randMember - choosing random friend from current group.
- rollLocation - return random location, based on areas set in db table

Commands and aliases defined in default:
- /start - nothing special
- /help - shows _help.html_ file
- /question - answering question
- /czy - alias for _/question czy_
- /roll - rolling things
- /coin - alias for _/roll coin_
- /who - random friend from current group
- /kto - random frien from current group
- /where - random location

## Things to 'roll'
There are some prepared things that can 'rolled':
- /roll pic - return random photo for current group - this option require to add group earlier (check in admin commands). Once you roll a picture on group and you are becoming Bot's friend on this group. Rolling pics is limited in time. Every time a random number of seconds (max 3600) must pass to roll another pic.
- /roll coin - return random sticker from db table with tag 'coin'
- /roll rps - return random sticker for rock-paper-scissors game
- /roll rpsls - as above but game is rock-paper-scissors-lizard-spock
- /roll 3d6+2 - rolling dices was the main function and idea to create this bot. Dice command should be build with the schema: [number of dices - max 100]letter d or D or k or K[number of dice sides] [modifier (+,-,*,/ and number)]. For capital letter D or K maximum value will be rolled again.

### Friends
Friends are special people which can do more things. To became a friend you must /roll pic on a group (only this group).
/who - you can be chosen by this command for a special task (/who will go for a beer?)
/addpic - you can add new group pictures (do it on private chat with bot). If you are friend on more than one group, you'll be asked to choose one. Then if there is a _special friend_ on group you'll have to choose if the photo is for him or for everyone. At the end just upload the photo into conversation.
*Special Friend* - when he doing _/roll pic_ pictures are taken from different folder. But it cost no time to roll again. To create a special friend, you must create a subfolder with user id as a name inside group folder in home directory.

## Admin commands
There are some commands which are allowed only for bot owner:
- /addchannel - adding current group to bot configuration. Bot will create a special folder in bot home. It will be used for keeping group photos. You can add _help.html_ file to this group - when somebody on group use command /help - this file will be used instead the main help file.
- /addsticker - you can add a sticker to db. After this command you'll be asked for adding a sticker. Just put in conversation. Then bot ask you for a category (ie. coin).
- /addrollsticker - when you create a new category (with command above) you can register it as a command to roll. Use this command with new category name as a parameter.
- /addanswer - you can add more answers and more questions
- /r - rebooting bot
- /u - print update information in console. Usefull thing for checking id's and similar things.

## Additional customization
- texts.py - you can change the default answers
- help.html - main help message
