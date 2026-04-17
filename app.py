"""
Aplicación de Hacking Ético - Dashboard
========================================
Aplicación web con Flask que integra 4 herramientas de ciberseguridad:
1. Escaneo de puertos lógicos
2. Generador de contraseñas seguras
3. Sniffing de red
4. Keylogger

NOTA: Esta aplicación es para fines educativos únicamente.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import threading

from modules.port_scanner import scan_ports
from modules.password_generator import generate_passwords
from modules.sniffer import start_sniffing, stop_sniffing, get_sniffer_status, get_captured_packets
from modules.keylogger import start_keylogger, stop_keylogger, get_keylogger_status, get_keylogger_log

app = Flask(__name__)

# ============================================================
# Ruta principal - Dashboard
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

# ============================================================
# 1. Escaneo de Puertos
# ============================================================
@app.route('/api/scan-ports', methods=['POST'])
def api_scan_ports():
    data = request.get_json()
    target = data.get('target', '')
    start_port = int(data.get('start_port', 1))
    end_port = int(data.get('end_port', 1024))

    if not target:
        return jsonify({'error': 'Se requiere una dirección IP o hostname'}), 400

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        return jsonify({'error': 'Rango de puertos inválido (1-65535)'}), 400

    try:
        results = scan_ports(target, start_port, end_port)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 2. Generador de Contraseñas Seguras
# ============================================================
@app.route('/api/generate-passwords', methods=['POST'])
def api_generate_passwords():
    data = request.get_json()
    length = int(data.get('length', 12))
    count = int(data.get('count', 1))

    if length < 8:
        return jsonify({'error': 'La longitud mínima de la contraseña es de 8 caracteres'}), 400

    if count < 1 or count > 100:
        return jsonify({'error': 'La cantidad debe ser entre 1 y 100'}), 400

    try:
        passwords = generate_passwords(length, count)
        return jsonify({'passwords': passwords})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 3. Sniffer de Red
# ============================================================
@app.route('/api/sniffer/start', methods=['POST'])
def api_start_sniffer():
    data = request.get_json()
    interface = data.get('interface', None)
    packet_count = int(data.get('packet_count', 50))
    filter_str = data.get('filter', '')

    try:
        result = start_sniffing(interface=interface, count=packet_count, filter_str=filter_str)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sniffer/stop', methods=['POST'])
def api_stop_sniffer():
    try:
        result = stop_sniffing()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sniffer/status', methods=['GET'])
def api_sniffer_status():
    try:
        status = get_sniffer_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sniffer/packets', methods=['GET'])
def api_sniffer_packets():
    try:
        packets = get_captured_packets()
        return jsonify({'packets': packets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# 4. Keylogger
# ============================================================
@app.route('/api/keylogger/start', methods=['POST'])
def api_start_keylogger():
    try:
        result = start_keylogger()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keylogger/stop', methods=['POST'])
def api_stop_keylogger():
    try:
        result = stop_keylogger()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keylogger/status', methods=['GET'])
def api_keylogger_status():
    try:
        status = get_keylogger_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keylogger/log', methods=['GET'])
def api_keylogger_log():
    try:
        log = get_keylogger_log()
        return jsonify(log)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# Iniciar la aplicación
# ============================================================
if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
