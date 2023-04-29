import telebot

#from Usuario import compra
from Objetos import Catalogo
from Administrador import log_in,sign_up

token = "6176731056:AAGDet-QoiPBc2EeUelbBpWkIHxmP0xaCwQ"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola!, bienvenido a mi ChatBot\n¿Desea ingresar como usuario o administrador?")

def handle_messages(messages):
    for message in messages:
        chatid = message.chat.id
        if message.content_type == 'text':
            text = message.text
            if text == "usuario":
                bot.send_message(chatid,"Desea realizar algun pedido?")
            if text == "si":
                bot.send_message(chatid,"¿Que producto desea adquirir?")
                bot.send_document(chatid, Catalogo(text))
            if text == "administrador":
                pass
                


bot.set_update_listener(handle_messages)

bot.infinity_polling()
