"""
Módulo 3: Sniffing de Red
===========================
Captura y analiza el tráfico de red usando Scapy.
Registra paquetes para diagnóstico y monitoreo.

NOTA: Requiere privilegios de administrador (sudo) para capturar paquetes.
"""

import threading
import json
import os
from datetime import datetime

try:
    from scapy.all import sniff as scapy_sniff, IP, TCP, UDP, Raw, ICMP, DNS, ARP, Ether
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# Estado global del sniffer
_sniffer_state = {
    'running': False,
    'thread': None,
    'packets': [],
    'start_time': None,
    'stop_event': threading.Event(),
    'interface': None,
    'packet_count': 0,
    'target_count': 50,
}

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')


def _packet_callback(packet):
    """
    Callback que se ejecuta por cada paquete capturado.
    Extrae información relevante del paquete.
    """
    global _sniffer_state

    if _sniffer_state['stop_event'].is_set():
        return

    packet_info = {
        'id': len(_sniffer_state['packets']) + 1,
        'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
        'length': len(packet),
    }

    # Capa Ethernet
    if packet.haslayer(Ether):
        packet_info['src_mac'] = packet[Ether].src
        packet_info['dst_mac'] = packet[Ether].dst

    # Capa IP
    if packet.haslayer(IP):
        packet_info['src_ip'] = packet[IP].src
        packet_info['dst_ip'] = packet[IP].dst
        packet_info['ttl'] = packet[IP].ttl
        packet_info['protocol_num'] = packet[IP].proto

    # Capa TCP
    if packet.haslayer(TCP):
        packet_info['protocol'] = 'TCP'
        packet_info['src_port'] = packet[TCP].sport
        packet_info['dst_port'] = packet[TCP].dport
        packet_info['tcp_flags'] = str(packet[TCP].flags)

        # Detectar protocolo de aplicación
        if packet[TCP].dport == 80 or packet[TCP].sport == 80:
            packet_info['app_protocol'] = 'HTTP'
        elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
            packet_info['app_protocol'] = 'HTTPS (Cifrado)'
        elif packet[TCP].dport == 21 or packet[TCP].sport == 21:
            packet_info['app_protocol'] = 'FTP'
        elif packet[TCP].dport == 22 or packet[TCP].sport == 22:
            packet_info['app_protocol'] = 'SSH (Cifrado)'
        elif packet[TCP].dport == 23 or packet[TCP].sport == 23:
            packet_info['app_protocol'] = 'Telnet (No seguro)'
        elif packet[TCP].dport == 25 or packet[TCP].sport == 25:
            packet_info['app_protocol'] = 'SMTP'
        else:
            packet_info['app_protocol'] = 'TCP'

    # Capa UDP
    elif packet.haslayer(UDP):
        packet_info['protocol'] = 'UDP'
        packet_info['src_port'] = packet[UDP].sport
        packet_info['dst_port'] = packet[UDP].dport

        if packet[UDP].dport == 53 or packet[UDP].sport == 53:
            packet_info['app_protocol'] = 'DNS'
        else:
            packet_info['app_protocol'] = 'UDP'

    # Capa ICMP
    elif packet.haslayer(ICMP):
        packet_info['protocol'] = 'ICMP'
        packet_info['app_protocol'] = 'ICMP'

    # ARP
    elif packet.haslayer(ARP):
        packet_info['protocol'] = 'ARP'
        packet_info['app_protocol'] = 'ARP'
        packet_info['src_ip'] = packet[ARP].psrc
        packet_info['dst_ip'] = packet[ARP].pdst

    else:
        packet_info['protocol'] = 'Otro'
        packet_info['app_protocol'] = 'Desconocido'

    # Datos en crudo (payload) - detectar texto plano
    if packet.haslayer(Raw):
        try:
            raw_data = packet[Raw].load.decode('utf-8', errors='ignore')
            if raw_data.isprintable() and len(raw_data.strip()) > 0:
                packet_info['payload'] = raw_data[:500]
                packet_info['payload_type'] = 'Texto Plano (¡No seguro!)'
            else:
                packet_info['payload'] = f'[Datos binarios - {len(packet[Raw].load)} bytes]'
                packet_info['payload_type'] = 'Binario/Cifrado'
        except Exception:
            packet_info['payload'] = f'[Datos - {len(packet[Raw].load)} bytes]'
            packet_info['payload_type'] = 'Binario/Cifrado'
    else:
        packet_info['payload'] = ''
        packet_info['payload_type'] = 'Sin datos'

    _sniffer_state['packets'].append(packet_info)
    _sniffer_state['packet_count'] += 1


def _sniff_thread(interface, count, filter_str):
    """
    Hilo de sniffing. Ejecuta la captura de paquetes.
    """
    global _sniffer_state

    try:
        kwargs = {
            'prn': _packet_callback,
            'store': False,
            'count': count,
            'stop_filter': lambda x: _sniffer_state['stop_event'].is_set(),
        }

        if interface:
            kwargs['iface'] = interface
        if filter_str:
            kwargs['filter'] = filter_str

        scapy_sniff(**kwargs)
    except Exception as e:
        _sniffer_state['error'] = str(e)
    finally:
        _sniffer_state['running'] = False
        # Guardar log al finalizar
        _save_log()


def _save_log():
    """
    Guarda los paquetes capturados en un archivo de log.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(LOG_DIR, f'sniffer_{timestamp}.json')

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'capture_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'interface': _sniffer_state['interface'],
                'total_packets': len(_sniffer_state['packets']),
                'packets': _sniffer_state['packets']
            }, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def start_sniffing(interface=None, count=50, filter_str=''):
    """
    Inicia la captura de paquetes en un hilo independiente.
    """
    global _sniffer_state

    if not SCAPY_AVAILABLE:
        return {'error': 'Scapy no está instalado. Ejecuta: pip install scapy'}

    if _sniffer_state['running']:
        return {'error': 'El sniffer ya está en ejecución'}

    _sniffer_state['running'] = True
    _sniffer_state['packets'] = []
    _sniffer_state['packet_count'] = 0
    _sniffer_state['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _sniffer_state['stop_event'].clear()
    _sniffer_state['interface'] = interface
    _sniffer_state['target_count'] = count
    _sniffer_state['error'] = None

    thread = threading.Thread(
        target=_sniff_thread,
        args=(interface, count, filter_str),
        daemon=True
    )
    thread.start()
    _sniffer_state['thread'] = thread

    return {
        'status': 'Sniffer iniciado',
        'interface': interface or 'Todas',
        'target_count': count,
        'filter': filter_str or 'Ninguno',
    }


def stop_sniffing():
    """
    Detiene la captura de paquetes.
    """
    global _sniffer_state

    if not _sniffer_state['running']:
        return {'status': 'El sniffer no está en ejecución'}

    _sniffer_state['stop_event'].set()
    _sniffer_state['running'] = False

    return {
        'status': 'Sniffer detenido',
        'packets_captured': len(_sniffer_state['packets']),
    }


def get_sniffer_status():
    """
    Obtiene el estado actual del sniffer.
    """
    return {
        'running': _sniffer_state['running'],
        'packets_captured': len(_sniffer_state['packets']),
        'target_count': _sniffer_state['target_count'],
        'start_time': _sniffer_state['start_time'],
        'interface': _sniffer_state['interface'] or 'Todas',
        'error': _sniffer_state.get('error'),
    }


def get_captured_packets():
    """
    Retorna los paquetes capturados hasta el momento.
    """
    return _sniffer_state['packets']
