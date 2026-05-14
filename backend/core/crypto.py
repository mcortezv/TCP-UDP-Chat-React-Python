import base64
import rsa

"""
Modulo con utilidades de cifrado RSA para la comunicacion TCP/UDP.
Se usan claves de 1024 bits (rapido de generar) y se cifra en bloques
de 80 bytes para soportar mensajes largos.
"""

# Tamano de cada bloque de texto a cifrar (en bytes).
# Para una llave de 1024 bits con padding PKCS#1, el limite es 117 bytes.
_BLOCK_SIZE = 80


def generate_keys():
    """
    Genera un par de claves RSA (publica, privada).
    """
    return rsa.newkeys(1024)


def export_pubkey(pubkey) -> str:
    """
    Convierte una clave publica a una cadena base64 para enviarla por la red.
    """
    return base64.b64encode(pubkey.save_pkcs1()).decode()


def import_pubkey(pubkey_b64: str):
    """
    Reconstruye una clave publica a partir de una cadena base64.
    """
    return rsa.PublicKey.load_pkcs1(base64.b64decode(pubkey_b64))


def encrypt_text(text: str, pubkey) -> str:
    """
    Cifra un texto con la clave publica del destinatario.
    Si el texto es mas largo que el bloque, lo divide y cifra cada parte.
    Regresa una cadena base64 con los bloques separados por '.'.
    """
    data = text.encode("utf-8")
    bloques = []
    for i in range(0, len(data), _BLOCK_SIZE):
        parte = data[i:i + _BLOCK_SIZE]
        cifrado = rsa.encrypt(parte, pubkey)
        bloques.append(base64.b64encode(cifrado).decode())
    return ".".join(bloques)


def decrypt_text(cifrado_b64: str, privkey) -> str:
    """
    Descifra un texto que viene en bloques base64 separados por '.'.
    Regresa el texto plano.
    """
    bloques = cifrado_b64.split(".")
    resultado = b""
    for bloque in bloques:
        cifrado = base64.b64decode(bloque)
        resultado += rsa.decrypt(cifrado, privkey)
    return resultado.decode("utf-8")
