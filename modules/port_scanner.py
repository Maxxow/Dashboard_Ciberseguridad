"""
Módulo 1: Escaneo de Puertos Lógicos
======================================
Escanea puertos TCP abiertos en un host remoto utilizando
la técnica de TCP Connect Scan con sockets.
"""

import socket
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Diccionario de servicios comunes por puerto
COMMON_SERVICES = {
    20: 'FTP-Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
    25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
    119: 'NNTP', 123: 'NTP', 135: 'MS-RPC', 139: 'NetBIOS',
    143: 'IMAP', 161: 'SNMP', 194: 'IRC', 443: 'HTTPS',
    445: 'SMB', 465: 'SMTPS', 514: 'Syslog', 587: 'SMTP-TLS',
    993: 'IMAPS', 995: 'POP3S', 1080: 'SOCKS', 1433: 'MSSQL',
    1434: 'MSSQL-UDP', 1521: 'Oracle', 1723: 'PPTP',
    3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
    5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Proxy',
    8443: 'HTTPS-Alt', 8888: 'HTTP-Alt', 27017: 'MongoDB',
}


def scan_single_port(target, port, timeout=1):
    """
    Escanea un solo puerto TCP en el host objetivo.
    Retorna información del puerto si está abierto, None si está cerrado.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()

        if result == 0:
            service = COMMON_SERVICES.get(port, 'Desconocido')
            # Intentar obtener el banner del servicio
            banner = grab_banner(target, port, timeout)
            return {
                'port': port,
                'state': 'Abierto',
                'service': service,
                'banner': banner
            }
        return None
    except socket.error:
        return None


def grab_banner(target, port, timeout=1):
    """
    Intenta obtener el banner de un servicio en un puerto abierto.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        sock.send(b'HEAD / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        return banner[:200] if banner else ''
    except Exception:
        return ''


def scan_ports(target, start_port=1, end_port=1024, max_threads=100):
    """
    Escanea un rango de puertos TCP en el host objetivo usando múltiples hilos.

    Args:
        target (str): IP o hostname del objetivo
        start_port (int): Puerto inicial del rango
        end_port (int): Puerto final del rango
        max_threads (int): Número máximo de hilos concurrentes

    Returns:
        dict: Resultados del escaneo con puertos abiertos y metadatos
    """
    # Resolver hostname
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        raise ValueError(f'No se pudo resolver el hostname: {target}')

    start_time = datetime.now()
    open_ports = []
    total_ports = end_port - start_port + 1

    # Escaneo con ThreadPoolExecutor para mayor velocidad
    with ThreadPoolExecutor(max_workers=min(max_threads, total_ports)) as executor:
        futures = {
            executor.submit(scan_single_port, target_ip, port): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Ordenar puertos abiertos por número
    open_ports.sort(key=lambda x: x['port'])

    return {
        'target': target,
        'target_ip': target_ip,
        'start_port': start_port,
        'end_port': end_port,
        'total_scanned': total_ports,
        'open_count': len(open_ports),
        'open_ports': open_ports,
        'scan_duration': round(duration, 2),
        'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
