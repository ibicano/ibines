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


# Devuelve el valor entero de un byte cuando el bit 7 indica el signo
def signed_value(byte):
    b = byte & 0x7F

    if byte & 0x80:
        return -b
    else:
        return b
