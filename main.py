import configparser,telebot,json
import os
from qiwipyapi import Wallet
from telebot import types, util
from threading import Thread
from time import sleep
from util import generate_random_password, renamer

keyboardcheck = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboardcheck.add(types.KeyboardButton("Проверить оплату"))
keyboardcheck.add(types.KeyboardButton("Отменить платеж"))

removekeyboard = types.ReplyKeyboardRemove()

config = configparser.ConfigParser()
config.read("config.ini")

TOKEN = config["telegram"]["token"]
OWNER_ID = config["telegram"]["owner"]
wallet_number = config["qiwi"]["wallet_number"]
QIWI_SEC_TOKEN = config["qiwi"]["QIWI_SEC_TOKEN"]
PRICE = config["price"]["price"]
print(f'===\nConfig is:\nOwner ID: {OWNER_ID}\nBot Token: {TOKEN}\nwallet_number: {wallet_number}\nQIWI_SEC_TOKEN: {QIWI_SEC_TOKEN}\n===')

wallet_p2p = Wallet(wallet_number, p2p_sec_key=QIWI_SEC_TOKEN)
bot = telebot.TeleBot(TOKEN)

def save_to_settings(name, password):
    try:
        open('/etc/ppp/chap-secrets','a').write(f'\n{name} pptpd {password} *')
        os.system('sudo service pptpd restart')
    except Exception as e:
        print(str(e))

def create_account_vpn(name, id):
    log = load_log(id)
    password = generate_random_password(10)
    log['buyed'].append({'ip':'18.117.182.83','username':renamer(name),'pass':password})
    save_log(log,id)
    save_to_settings(renamer(name), password)
    return 

def check_billing(message, name: str):
    print('Getted name: '+name)
    for x in range(240):
        log = load_log(message.from_user.id)
        if log['billid'] != '':
            status = wallet_p2p.invoice_status(bill_id=log['billid'])
            if status['status']['value'] == 'PAID':
                create_account_vpn(name, message.from_user.id)
                bot.send_message(message.chat.id,'Мы увидили ваш платеж, данные от VPN вы можете просмотреть через /myvpns')
                return
            else:
                sleep(60)
        else:
            return
    return



def load_log(log):
    with open(f'logs/{str(log)}.json','r',encoding='utf-8') as f:
        data = json.load(f)
        return data
def save_log(exchanges: dict, id):
    temp = load_log(id)
    temp.update(exchanges)
    with open(f'logs/{id}.json','w',encoding='utf-8') as file:
        json.dump(temp, file, ensure_ascii=False,indent=4)
        return True
    pass

def HaveLog(id):
    try:
        open('logs/'+str(id)+'.json','r',encoding='utf-8').read()
        return True
    except Exception as e:
        return False

def save_example_log(id):
    with open(f'logs/{id}.json','w',encoding='utf-8') as file:
        json.dump({
            'buyed':[],
            'lastname':'',
            'billid': '',
            'buyprocces': False
        }, file, ensure_ascii=False,indent=4)
    return True

@bot.message_handler(commands=["start"])
def connectss(message):
    if not HaveLog(message.from_user.id):
        save_example_log(message.from_user.id)
    bot.send_message(message.chat.id, f'Здравствуй, {message.from_user.first_name}!👋\nЯ бот для продажи VPN сервисов от @skiste.\nДля покупки - /buy\nДля справки - /help\nДля купленных VPN аккаунтов - /myvpns\n\nДАННЫЙ VPN НЕ РАБОТАЕТ ДЛЯ АЙФОНОВ, Я РАБОТАЮ НАД ЭТИМ')

@bot.message_handler(commands=["help"])
def connectss(message):
    bot.send_message(message.chat.id, 'Данный бот, это бот для продажи VPN сервисов от амазона. Сервер стоит в США. Из скорости, до 6мбит\с на вход и выход\n\nЦена составляет всего **100 рублей**\n\nВ случае неработоспособности VPN (что в теории не возможно, но мало ли) писать @skiste\n\nДля подключения на:\nWindows - https://clck.ru/sY83o (протокол PPTP)', parse_mode="Markdown")

@bot.message_handler(commands=["myvpns"])
def connectss(message):
    temp = load_log(message.from_user.id)
    if temp['buyed'] == []:
        bot.send_message(message.chat.id, 'У вас не куплено ни одного аккаунта, исправить это можно через - /buy !')
    else:
        text = ''
        for x in temp['buyed']:
            text = text + '`' +x['ip'] + '` - IP\n`' + x['username'] + '` - Username\n`' + x['pass'] +'` - Password\n---\n'
        bot.send_message(message.chat.id, text[:-5], parse_mode='Markdown')

@bot.message_handler(commands=["stoop"])
def connectss(message):
    if str(message.from_user.id) == OWNER_ID:
        os.exit()
@bot.message_handler(commands=["buy"])
def connectss(message):
    save_log({'buyprocces':False},message.from_user.id)
    log = load_log(message.from_user.id)
    if not log['buyprocces']:
        bot.send_message(message.chat.id, 'Введите желаемое имя учетной записи для VPN (без спец символов и пробелов, только буквы):')
        save_log({'buyprocces':True},message.from_user.id)
        

@bot.message_handler(content_types='text')
def connectss(message):
    log = load_log(message.from_user.id)
    if log['buyprocces']:
        invoice = wallet_p2p.create_invoice(value=int(PRICE))
        print(invoice["payUrl"])
        bot.send_message(message.chat.id, f'Отличное имя!\nТеперь осталось лишь заплатить:\n{invoice["payUrl"]}',reply_markup=keyboardcheck)
        save_log({'lastname':message.text,'buyprocces':False,'billid':invoice['billId']},message.from_user.id)
        Thread(target=check_billing,args=(message,message.text,)).start()
    elif message.text == "Проверить оплату":
        status = wallet_p2p.invoice_status(bill_id=log['billid'])
        print(status)
        if status['status']['value'] == 'WAITING':
            bot.send_message(message.chat.id, 'Платеж к сожалению все еще не прошел')
            return
        elif status['status']['value'] == 'PAID':
            bot.send_message(message.chat.id, 'Видим ваш платеж, работаем над созданием аккаунта')
    elif message.text == 'Отменить платеж':
        wallet_p2p.cancel_invoice(bill_id=log['billid'])
        bot.send_message(message.chat.id, 'Платеж был отменен ;c', reply_markup=removekeyboard)
        save_log({'billid':'','lastname':''},message.from_user.id)
        return


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(str(e))
