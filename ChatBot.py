import csv
import random
import telebot

TOKEN = "6176731056:AAGDet-QoiPBc2EeUelbBpWkIHxmP0xaCwQ"
bot = telebot.TeleBot(TOKEN)

admin_pin = "1065562454"  # Pin de administrador (puedes cambiarlo)
intentos_admin = {}
usuarios_registrados = set()


@bot.message_handler(commands=['admin'])
def modo_administrador(message):
    chat_id = message.chat.id
    
    if chat_id not in intentos_admin:
        intentos_admin[chat_id] = 0
    
    if intentos_admin[chat_id] >= 5:
        bot.send_message(chat_id, "Has superado el límite de intentos. Vuelve a iniciar sesión.")
        intentos_admin[chat_id] = 0
        return
    
    if intentos_admin[chat_id] == 0:
        bot.send_message(chat_id, "Ingresa el PIN de administrador:")
    
    bot.register_next_step_handler(message, verificar_pin_administrador)

def verificar_pin_administrador(message):
    chat_id = message.chat.id
    pin_ingresado = message.text
    
    if pin_ingresado == admin_pin:
        intentos_admin[chat_id] = 0
        bot.send_message(chat_id, "Acceso concedido. Modo Administrador activado.")
        admin_menu(message)  # Mostrar el menú de administrador
    else:
        intentos_admin[chat_id] += 1
        bot.send_message(chat_id, "PIN incorrecto. Intenta nuevamente.")
        bot.send_message(chat_id, f"Intento {intentos_admin[chat_id]} de 5")
        bot.register_next_step_handler(message, verificar_pin_administrador)
        
# Función para registrar un producto
def agregar_producto(nombre, precio, cantidad):
    referencia = generar_referencia()
    with open('productos.csv', 'a', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow([nombre, precio, cantidad, referencia])

@bot.message_handler(commands=['registrar'])
def registrar_producto(message):
    bot.send_message(message.chat.id, "Ingrese el nombre del producto:")
    bot.register_next_step_handler(message, obtener_nombre_producto)

def obtener_nombre_producto(message):
    nombre = message.text
    bot.send_message(message.chat.id, "Ingrese el precio del producto:")
    bot.register_next_step_handler(message, obtener_precio_producto, nombre)


def obtener_precio_producto(message, nombre):
    precio = message.text
    bot.send_message(message.chat.id, "Ingrese la cantidad del producto:")
    bot.register_next_step_handler(message, obtener_cantidad_producto, nombre, precio)

def obtener_cantidad_producto(message, nombre, precio):
    cantidad = message.text
    agregar_producto(nombre, precio, cantidad)
    bot.send_message(message.chat.id, "Producto registrado exitosamente.")

# Función para generar una referencia aleatoria única
def generar_referencia():
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        referencias = set([row[3] for row in reader if len(row) > 3])
    while True:
        referencia = str(random.randint(1000, 9999))
        if referencia not in referencias:
            return referencia

# Función para mostrar los productos registrados
def productos():
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        productos = list(reader)
    if len(productos) > 0:
        mensaje = "Productos registrados:\n"
        for producto in productos:
            if len(producto) >= 4:
                mensaje += f"-Nombre: {producto[0]}\n\n--->Precio: ${producto[1]} pesos\n--->Cantidad: {producto[2]}\n--->Referencia: {producto[3]}\n\n"
            else:
                mensaje += "Producto incompleto\n"
    else:
        mensaje = "No hay productos registrados."
    return mensaje

@bot.message_handler(commands=['mostrar'])
def mostrar(message):
    producto = productos()
    bot.send_message(message.chat.id, producto)

# Función para borrar un producto por su referencia
def borrar_producto(referencia):
    productos = []
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] != referencia:
                productos.append(row)

    with open('productos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(productos)

@bot.message_handler(commands=['borrar'])
def borrar(message):
    bot.send_message(message.chat.id, "Ingrese la referencia del producto que desea borrar:")
    bot.register_next_step_handler(message, confirmar_borrar_producto)

def obtener_informacion_producto(referencia):
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] == referencia:
                nombre = row[0]
                precio = row[1]
                cantidad = row[2]
                return f"Nombre: {nombre}\nPrecio: ${precio} pesos\nCantidad: {cantidad}"
    return "Producto no encontrado"

def confirmar_borrar_producto(message):
    referencia = message.text
    # Mostrar información del producto antes de borrarlo
    producto = obtener_informacion_producto(referencia)  # Implementa esta función para obtener la información del producto
    bot.send_message(message.chat.id, f"¿Estás seguro que deseas borrar el producto?\n\n{producto}")
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Sí', 'No')
    bot.send_message(message.chat.id, "Por favor, elige una opción:", reply_markup=markup)
    bot.register_next_step_handler(message, confirmacion_borrar_producto, referencia)

def confirmacion_borrar_producto(message, referencia):
    if message.text.lower() == 'sí':
        borrar_producto(referencia)  # Llama a la función de borrar producto en administrador.py
        bot.send_message(message.chat.id, "Producto borrado exitosamente.")
    else:
        bot.send_message(message.chat.id, "Operación cancelada.")

# Función para editar un producto por su referencia
def editar_producto(referencia, nuevo_precio, nueva_cantidad):
    productos = []
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] == referencia:
                row[1] = str(nuevo_precio)
                row[2] = str(nueva_cantidad)
            productos.append(row)

    with open('productos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(productos)

@bot.message_handler(commands=['editar'])
def editar(message):
    bot.send_message(message.chat.id, "Ingrese la referencia del producto que desea editar:")
    bot.register_next_step_handler(message, verificar_producto_existente)

def verificar_producto_existente(message):
    referencia = message.text
    if verificar_producto(referencia):
        bot.send_message(message.chat.id, "Ingrese el nuevo precio del producto:")
        bot.register_next_step_handler(message, obtener_nuevo_precio, referencia)
    else:
        bot.send_message(message.chat.id, "El producto ingresado no existe.")

def obtener_nuevo_precio(message, referencia):
    nuevo_precio = message.text
    bot.send_message(message.chat.id, "Ingrese la nueva cantidad del producto:")
    bot.register_next_step_handler(message, obtener_nueva_cantidad, referencia, nuevo_precio)

def obtener_nueva_cantidad(message, referencia, nuevo_precio):
    nueva_cantidad = message.text
    editar_producto(referencia, nuevo_precio, nueva_cantidad)  # Llama a la función de editar producto en administrador.py
    bot.send_message(message.chat.id, "Producto editado exitosamente.")

# Funciones del modo usuario

# Función para registrar un usuario

def registrar_usuario(nombre, direccion, correo, identificacion, edad):
    with open('usuarios.csv', 'a', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow([nombre, direccion, correo, identificacion, edad])


@bot.message_handler(commands=['registro'])
def registrar(message):
    bot.send_message(message.chat.id, "Ingrese su nombre:")
    bot.register_next_step_handler(message, obtener_nombre_usuario)

def obtener_nombre_usuario(message):
    nombre = message.text
    bot.send_message(message.chat.id, "Ingrese su dirección:")
    bot.register_next_step_handler(message, obtener_direccion_usuario, nombre)

def obtener_direccion_usuario(message, nombre):
    direccion = message.text
    bot.send_message(message.chat.id, "Ingrese su correo:")
    bot.register_next_step_handler(message, obtener_correo_usuario, nombre, direccion)

def obtener_correo_usuario(message, nombre, direccion):
    correo = message.text
    bot.send_message(message.chat.id, "Ingrese su identificacion:")
    bot.register_next_step_handler(message, obtener_identificacion_usuario, nombre, direccion, correo)

def obtener_identificacion_usuario(message, nombre, direccion, correo):
    identificacion = message.text
    if verificar_identificacion(identificacion):
        bot.send_message(message.chat.id, "El número de identificación ya está registrado.")
        bot.send_message(message.chat.id, "Ingrese su identificacion:")
        bot.register_next_step_handler(message, obtener_identificacion_usuario, nombre, direccion, correo)
    else:
        bot.send_message(message.chat.id, "Ingrese su edad:")
        bot.register_next_step_handler(message, obtener_edad_usuario, nombre, direccion, correo, identificacion)

def obtener_edad_usuario(message, nombre, direccion, correo, identificacion):
    edad = message.text
    registrar_usuario(nombre, direccion, correo, identificacion, edad)
    bot.send_message(message.chat.id, "Usuario registrado exitosamente.")

def verificar_identificacion(identificacion):
    with open('usuarios.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] == identificacion: 
                return True
    return False

# Función para mostrar todos los productos
def mostrar_todos_los_productos():
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        productos = list(reader)
    if len(productos) > 0:
        mensaje = "Productos disponibles:\n"
        for producto in productos:
            mensaje += f"-Nombre: {producto[0]}\n\n--->Precio: ${producto[1]} pesos\n--->Cantidad: {producto[2]}\n--->Referencia: {producto[3]}\n\n"
    else:
        mensaje = "No hay productos disponibles."
    return mensaje


@bot.message_handler(commands=['productos'])
def productos_disponibles(message):
    productos = mostrar_todos_los_productos()
    bot.send_message(message.chat.id, productos)

# Función para realizar un pedido
def realizar_pedido(message, identificacion, producto, cantidad):
    # Verificar si el producto existe
    if not verificar_producto(producto):
        bot.send_message(message.chat.id, "El producto ingresado no existe.")
        return
    
    referencia = generar_referencia()
    with open('pedidos.csv', 'a', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow([identificacion, producto, cantidad, referencia])

    # Actualizar la cantidad del producto en productos.csv
    productos = []
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[0] == producto:
                nombre = row[0]
                precio = row[1]
                nueva_cantidad = int(row[2]) - int(cantidad)
                referencia = row[3]
                row = [nombre, precio, str(nueva_cantidad),referencia]
            productos.append(row)

    with open('productos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(productos)

    bot.send_message(message.chat.id, "Pedido realizado exitosamente.")

def verificar_producto(producto):
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[0] == producto:
                return True
    return False

@bot.message_handler(commands=['pedir'])
def modo_usuario(message):
    bot.send_message(message.chat.id, "Ingrese su identificacion:")
    bot.register_next_step_handler(message, obtener_pedido)

def obtener_pedido(message):
    identificacion = message.text
    bot.send_message(message.chat.id, "Ingrese el producto que quiere pedir:")
    bot.register_next_step_handler(message, obtener_cantidad_pedido, identificacion)

def obtener_cantidad_pedido(message, identificacion):
    producto = message.text
    # Verificar si el producto existe antes de continuar
    if not verificar_producto(producto):
        bot.send_message(message.chat.id, "El producto ingresado no existe.")
        return

    bot.send_message(message.chat.id, "Ingrese cuantos articulos desea:")
    bot.register_next_step_handler(message, terminar_pedido, identificacion, producto)

def terminar_pedido(message, identificacion, producto):
    cantidad = message.text
    realizar_pedido(message, identificacion, producto, cantidad)

# Función para cancelar un pedido por su referencia
def cancelar_pedido(referencia):
    pedidos = []
    with open('pedidos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[4] != referencia:
                pedidos.append(row)

    with open('pedidos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(pedidos)

@bot.message_handler(commands=['cancelar'])
def cancelar_pedido_usuario(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Ingrese la referencia del pedido que desea cancelar:")
    bot.register_next_step_handler(message, confirmar_cancelar_pedido)

def cancelar_pedido(referencia):
    pedidos = []
    with open('pedidos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] != referencia:
                pedidos.append(row)

    with open('pedidos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(pedidos)

def obtener_informacion_pedido(referencia):
    with open('pedidos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)

        with open('usuarios.csv', 'r') as usuario_csv:
            read = csv.reader(usuario_csv)
            users = list(read)

            for row in reader:
                for user in users:
                    if row[3] == referencia:
                        identificacion = row[0]
                        usuario = user[0]
                        direccion = user[1]
                        producto = row[1]
                        cantidad = row[2]
                        return f"Identificacion: {identificacion}\nUsuario: {usuario}\nDireccion: {direccion}\nProducto: {producto}\nCantidad: {cantidad}"

    return "Pedido no encontrado"

def confirmar_cancelar_pedido(message):
    chat_id = message.chat.id
    referencia = message.text

    # Mostrar información del pedido antes de cancelarlo
    pedido = obtener_informacion_pedido(referencia)

    if pedido == "Pedido no encontrado":
        bot.send_message(chat_id, "El pedido no existe.")
    else:
        bot.send_message(chat_id, f"¿Estás seguro que deseas cancelar el pedido?\n\n{pedido}")
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row('Sí', 'No')
        bot.send_message(chat_id, "Por favor, elige una opción:", reply_markup=markup)
        bot.register_next_step_handler(message, confirmacion_cancelar_pedido, referencia)

def confirmacion_cancelar_pedido(message, referencia):
    chat_id = message.chat.id
    if message.text.lower() == 'sí':
        cancelar_pedido(referencia)
        bot.send_message(chat_id, "Pedido cancelado exitosamente.")
    else:
        bot.send_message(chat_id, "Operación cancelada.")

# Funcion para mostrar los pedidos del usuario
@bot.message_handler(commands=['historial'])
def pedir_identificacion(message):
    bot.send_message(message.chat.id, "Por favor, ingrese su identificación:")
    bot.register_next_step_handler(message, mostrar_historial)


def mostrar_historial(message):
    identificacion = message.text
    historial = obtener_historial(identificacion)

    if historial:
        bot.send_message(message.chat.id, historial)
    else:
        bot.send_message(message.chat.id, "No se encontró historial de compras para esa identificación.")

def obtener_historial(identificacion):
    if validar_identificacion_pedido(identificacion):
        with open('pedidos.csv', 'r') as pedido_csv:
            reader = csv.reader(pedido_csv)
            pedidos = list(reader)

        with open('usuarios.csv', 'r') as usuario_csv:
            read = csv.reader(usuario_csv)
            users = list(read)

            if len(pedidos) > 0:
                mensaje = "Historial de pedidos:\n"
                for pedido in pedidos:
                    for user in users:
                        if identificacion == user[3]:
                            if pedido[0] == user[3]:
                                mensaje += f"Nombre: {user[0]}\n---> Direccion: {user[1]}\n---> Producto: {pedido[1]}\n---> Cantidad: {pedido[2]}\n---> Referencia: {pedido[3]}\n"
                return mensaje


    return None

def validar_identificacion_pedido(identificacion):
    with open('pedidos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[0] == identificacion:
                return True
    return False

@bot.message_handler(commands=['info'])
def informacion(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Ver mi información'))
    bot.send_message(chat_id, "¿Qué te gustaría hacer?", reply_markup=markup)
    bot.register_next_step_handler(message, obtener_identificacion)

def obtener_identificacion(message):
    chat_id = message.chat.id
    if message.text == 'Ver mi información':
        bot.send_message(chat_id, "Por favor, ingresa tu identificación:")
        bot.register_next_step_handler(message, mostrar_informacion_usuario)
    else:
        bot.send_message(chat_id, "Comando no reconocido.")
        # Mostrar el menú de usuario registrado
        informacion(message)

def mostrar_informacion_usuario(message):
    chat_id = message.chat.id
    identificacion = message.text
    
    with open('usuarios.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[3] == identificacion:
                nombre = row[0]
                direccion = row[1]
                correo = row[2]
                identificacion = row[3]
                edad = row[4]
                break
        else:
            nombre = "Desconocido"
            direccion = "Desconocida"
            correo = "Desconocido"
            edad = "Desconocida"
            identificacion = "Desconocido"
    
    mensaje = f"Información del usuario:\n\nNombre: {nombre}\nIdentificacion: {identificacion}\nCorreo electrónico: {correo}\nDireccion: {direccion}\nEdad: {edad} años"
    bot.send_message(chat_id, mensaje)


def admin_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/registrar', '/mostrar', '/editar', '/borrar')
    bot.send_message(message.chat.id, "Menú de administrador:", reply_markup=markup)

@bot.message_handler(commands=['user'])
def user_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)  # Especifica row_width=3 para mostrar 3 elementos por fila
    markup.add('/registro', '/productos')
    markup.add('/pedir', '/cancelar', '/historial')
    markup.add('/info')
    bot.send_message(message.chat.id, "Menú de usuario:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Bienvenido al sistema de gestión de productos.\nPresione /admin para entrar en modo administrador\nPresione /user para entrar en modo usuario")
# Función para verificar si el usuario es administrador
@bot.message_handler(commands=['User'])
def modo_usuario(message):
    comando = message.text[1:]  # Obtener el comando sin el "/"
    
    if comando == 'User':
        # Modo Usuario
        # Agrega aquí la lógica y las funciones correspondientes al modo usuario.
        bot.send_message(message.chat.id, "Modo Usuario activado.")
        user_menu(message)  # Mostrar el menú de usuario
    else:
        # Comando inválido
        bot.send_message(message.chat.id, "Comando inválido. Por favor, ingresa /User o /Admin.")

bot.polling()
bot.infinity_polling()
