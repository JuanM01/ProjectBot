import telebot
import Administrador

token = "6176731056:AAGDet-QoiPBc2EeUelbBpWkIHxmP0xaCwQ"
PinAdmin = 123456
bot = telebot.TeleBot(token)

productos = {}
clientes = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Bienvenido, Disfruta de tu experiencia")
    bot.send_message(message.chat.id,"utilice el comando /admin para entrar en modo administrador o continue como usuario para registrarse o realizar alguna compra")

@bot.message_handler(commands=['admin'])
def admin(message):
	msg = bot.send_message(message.chat.id,"Ingrese su pin de administrador para acceder al modo administrador")
	bot.register_next_step_handler(msg, ver)
	
@bot.message_handler(content_types=["text"])
def ver(message):
	Pin = int(message.text)
	if Pin == PinAdmin:
		msg = bot.send_message(message.chat.id,"Bienvenido señor administrador")
		bot.register_next_step_handler(msg, Menú_Admin)
	else:
		msg = bot.send_message(message.chat.id,"Lo sentimos, pin incorrecto")
		bot.register_next_step_handler(msg, ver)

@bot.message_handler(content_types=["text","number"])
def Menú_Admin(message):
    if message.text.isdigit():
        msg = bot.send_message(message.chat.id,"¿Que desea hacer?\n1)Registrar un producto\n2)Modificar un producto\n3)Eliminar un producto\n4)Ver productos existentes")
        bot.register_next_step_handler(msg, Options)
	    

@bot.message_handler(content_types=["number"])
def Options(message):
	OP = int(message.text)
	if OP == 1:
		pass
	elif OP == 2:
		pass
	elif OP == 3:
		pass
	elif OP == 4:
		pass
	else:
		msg = bot.send_message(message.chat.id,"Por favor, Digite una opcion valida")
		bot.register_next_step_handler(msg,Options)

@bot.message_handler(content_types=["text"])
def mensajes_text(message):
	if message.text.startswith("/"):
		bot.send_message(message.chat.id,"comando no disponible")

bot.infinity_polling()