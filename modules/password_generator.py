"""
Módulo 2: Generador de Contraseñas Seguras
=============================================
Genera contraseñas seguras de longitud variable combinando
letras (mayúsculas y minúsculas), números y caracteres especiales.
Longitud mínima: 8 caracteres.
"""

import secrets
import string
import math


def calculate_entropy(password):
    """
    Calcula la entropía de una contraseña en bits.
    Mayor entropía = contraseña más segura.
    """
    charset_size = 0
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digits = any(c in string.digits for c in password)
    has_special = any(c in string.punctuation for c in password)

    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_digits:
        charset_size += 10
    if has_special:
        charset_size += len(string.punctuation)

    if charset_size == 0:
        return 0

    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)


def get_strength(entropy):
    """
    Determina la fortaleza de la contraseña basada en su entropía.
    """
    if entropy < 36:
        return {'level': 'Muy Débil', 'color': '#ef4444', 'score': 1}
    elif entropy < 60:
        return {'level': 'Débil', 'color': '#f97316', 'score': 2}
    elif entropy < 80:
        return {'level': 'Moderada', 'color': '#eab308', 'score': 3}
    elif entropy < 100:
        return {'level': 'Fuerte', 'color': '#22c55e', 'score': 4}
    else:
        return {'level': 'Muy Fuerte', 'color': '#06b6d4', 'score': 5}


def generate_single_password(length):
    """
    Genera una sola contraseña segura que garantiza contener
    al menos una letra mayúscula, una minúscula, un número
    y un carácter especial.

    Args:
        length (int): Longitud de la contraseña (mínimo 8)

    Returns:
        dict: Contraseña generada con metadatos de seguridad
    """
    if length < 8:
        raise ValueError('La longitud mínima de la contraseña es de 8 caracteres')

    # Caracteres disponibles
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = string.punctuation

    # Garantizar al menos uno de cada tipo
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]

    # Rellenar el resto con caracteres aleatorios de todos los conjuntos
    all_chars = lowercase + uppercase + digits + special
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))

    # Mezclar la contraseña para que los caracteres garantizados
    # no estén siempre al inicio
    secrets.SystemRandom().shuffle(password)
    password_str = ''.join(password)

    # Calcular métricas de seguridad
    entropy = calculate_entropy(password_str)
    strength = get_strength(entropy)

    return {
        'password': password_str,
        'length': length,
        'entropy': entropy,
        'strength': strength,
        'has_lowercase': True,
        'has_uppercase': True,
        'has_digits': True,
        'has_special': True,
    }


def generate_passwords(length, count):
    """
    Genera múltiples contraseñas seguras.

    Args:
        length (int): Longitud de cada contraseña (mínimo 8)
        count (int): Cantidad de contraseñas a generar (1-100)

    Returns:
        list: Lista de diccionarios con las contraseñas y sus metadatos
    """
    if length < 8:
        raise ValueError('La longitud mínima de la contraseña es de 8 caracteres')

    if count < 1 or count > 100:
        raise ValueError('La cantidad debe ser entre 1 y 100')

    passwords = []
    for _ in range(count):
        pwd = generate_single_password(length)
        passwords.append(pwd)

    return passwords
