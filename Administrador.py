import csv

def agregar_producto(nombre, precio, cantidad,referencia):
    with open('productos.csv', 'a', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow([nombre, precio, cantidad,referencia])

def mostrar_productos():
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            print(f'Producto: {row[0]}, Precio: {row[1]}, Cantidad: {row[2]},referencia: {row[3]}')

def borrar_producto(nombre):
    productos = []
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[0] != nombre:
                productos.append(row)

    with open('productos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(productos)

def editar_producto(nombre, nuevo_precio, nueva_cantidad,nueva_referencia):
    productos = []
    with open('productos.csv', 'r') as archivo_csv:
        reader = csv.reader(archivo_csv)
        for row in reader:
            if row[0] == nombre:
                row[1] = str(nuevo_precio)
                row[2] = str(nueva_cantidad)
                row[3] = str(nueva_referencia)
            productos.append(row)

    with open('productos.csv', 'w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerows(productos)