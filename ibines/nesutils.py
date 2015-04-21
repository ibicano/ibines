# -*- coding: utf-8 *-*

###############################################################################
# nesutils.py
#
# Módulo con distintas funciones útiles
###############################################################################

# Devuelve el valor del bit indicado por "bit_number" de la palabra
# especificada por "word"
def get_bit(word, bit_number):
    return (word >> bit_number) & 0x00000001


# Establece el bit especificado por "bit_number" al valor especificado en
# "bit_value" en la palabra "word"
def set_bit(word, bit_number, bit_value):
    mask = 0x00000001
    mask = mask << bit_number
    if bit_value:
        result = word | mask
    else:
        result = word & (mask ^ 0xFFFFFFFF)

    return result


# Devuelve el valor entero de un byte en complemento a 2
def c2_to_int(byte):
    if byte & 0x80:
        return -(0x100 - byte)
    else:
        return byte

# Convierte un entero a complemento a 2
def int_to_c2(n):
    if n >= 0:
        c2 = n
    else:
        c2 = (~n + 1) & 0xFF

    return c2

