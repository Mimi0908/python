import random

caracteres = "+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

longitud = int(input("Introduce la longitud que deseas que tenga la contrasena: "))

contrasena = ""

for i in range(longitud):
    contrasena += random.choice(caracteres)

print("Contrasena generada: ", contrasena)

