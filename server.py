#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serveur final corrigé pour Simulateur de Scope Médical
Version sans erreur de formatage
"""

try:
    import http.server as BaseHTTPServer
    import socketserver
    from urllib.parse import urlparse
    from http.server import SimpleHTTPRequestHandler
except ImportError:
    import BaseHTTPServer
    import SocketServer as socketserver
    from urlparse import urlparse
    from SimpleHTTPServer import SimpleHTTPRequestHandler

import json
import threading
import time
import socket
import os
import sys
import webbrowser

# Configuration globale
PORT = 3000
SERVER_IP = "0.0.0.0"

# État des signes vitaux
vitals = {
    'current': {'fc': 75, 'spo2': 98, 'fr': 16},
    'target': {'fc': 75, 'spo2': 98, 'fr': 16},
    'mobile_connected': False,
    'last_mobile_ping': 0
}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class ScopeHandler(SimpleHTTPRequestHandler):
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self.serve_scope_page()
        elif path == '/mobile':
            self.serve_mobile_page()
        elif path == '/api/vitals':
            self.serve_api()
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == '/api/update':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            
            try:
                if sys.version_info[0] >= 3:
                    json_data = json.loads(data.decode('utf-8'))
                else:
                    json_data = json.loads(data)
                
                # Marquer mobile comme connecte
                vitals['last_mobile_ping'] = time.time()
                vitals['mobile_connected'] = True
                
                # Mettre à jour les valeurs
                if 'fc' in json_data:
                    vitals['target']['fc'] = int(json_data['fc'])
                if 'spo2' in json_data:
                    vitals['target']['spo2'] = int(json_data['spo2'])
                if 'fr' in json_data:
                    vitals['target']['fr'] = int(json_data['fr'])
                
                print("📱 Mise à jour: FC={}, SpO2={}, FR={}".format(
                    vitals['target']['fc'], vitals['target']['spo2'], vitals['target']['fr']))
                
                self.send_json({'success': True})
            except:
                self.send_error(400)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        json_str = json.dumps(data)
        if sys.version_info[0] >= 3:
            self.wfile.write(json_str.encode('utf-8'))
        else:
            self.wfile.write(json_str)
    
    def serve_api(self):
        # Vérifier si mobile encore connecté
        if time.time() - vitals['last_mobile_ping'] > 10:
            vitals['mobile_connected'] = False
        
        self.send_json(vitals)
    
    def serve_scope_page(self):
        local_ip = get_local_ip()
        mobile_url = "http://{}:{}/mobile".format(local_ip, PORT)
        
        # HTML sans problème de formatage
        html_part1 = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>🎯 Simulateur de Scope Médical</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .heart-beat { animation: heartbeat 1s infinite; }
        @keyframes heartbeat { 0%, 50% { transform: scale(1); } 25% { transform: scale(1.1); } }
        .vital-display { font-family: 'Courier New', monospace; text-shadow: 0 0 10px currentColor; }
        .waveform { background: linear-gradient(to right, transparent 0%, transparent 10px, rgba(75, 85, 99, 0.3) 10px, rgba(75, 85, 99, 0.3) 11px, transparent 11px); background-size: 20px 100%; }
    </style>
</head>
<body class="bg-black text-white min-h-screen">
    <div id="connection-info" class="absolute top-2 left-2 text-xs bg-slate-800 p-2 rounded text-slate-400">
        <div>📱 Mobile: <a href="''' + mobile_url + '''" class="text-blue-400 underline">''' + mobile_url + '''</a></div>
        <div id="status">🔗 <span class="text-yellow-400">En attente...</span></div>
    </div>
    
    <div class="h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-6xl h-[700px] bg-black rounded-lg border-2 border-slate-700 grid grid-cols-[3fr,1fr] gap-2 p-2">
            
            <div class="grid grid-rows-3 gap-1">
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-green-400 text-sm mb-1">ECG (FC)</div><div class="h-20 bg-black rounded"></div></div>
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-cyan-400 text-sm mb-1">Pleth (SpO₂)</div><div class="h-20 bg-black rounded"></div></div>
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-yellow-300 text-sm mb-1">Resp (FR)</div><div class="h-20 bg-black rounded"></div></div>
            </div>
            
            <div class="bg-slate-800 rounded p-4 flex flex-col justify-around">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-6 h-6 mr-2 text-green-400 heart-beat">💚</div>
                        <div><span class="text-green-400 font-medium">FC</span><span class="text-xs text-green-400 opacity-80 ml-1">bpm</span></div>
                    </div>
                    <div id="fc-display" class="text-4xl font-bold text-green-400 vital-display">75</div>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-6 h-6 mr-2 text-cyan-400">🌊</div>
                        <div><span class="text-cyan-400 font-medium">SpO₂</span><span class="text-xs text-cyan-400 opacity-80 ml-1">%</span></div>
                    </div>
                    <div id="spo2-display" class="text-4xl font-bold text-cyan-400 vital-display">98</div>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-6 h-6 mr-2 text-yellow-300">〰️</div>
                        <div><span class="text-yellow-300 font-medium">FR</span><span class="text-xs text-yellow-300 opacity-80 ml-1">/min</span></div>
                    </div>
                    <div id="fr-display" class="text-4xl font-bold text-yellow-300 vital-display">16</div>
                </div>
                
                <div class="flex items-center justify-between pt-4">
                    <div><span class="text-lime-400 font-medium">PNI</span><span class="text-xs text-lime-400 opacity-80 ml-1">mmHg</span></div>
                    <div class="text-3xl font-bold text-lime-400 vital-display">120/80</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function updateDisplay() {
            fetch('/api/vitals')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('fc-display').textContent = data.current.fc;
                    document.getElementById('spo2-display').textContent = data.current.spo2;
                    document.getElementById('fr-display').textContent = data.current.fr;
                    
                    const status = document.getElementById('status');
                    if (data.mobile_connected) {
                        status.innerHTML = '📱 <span class="text-green-400">Mobile connecté</span>';
                    } else {
                        status.innerHTML = '🔗 <span class="text-yellow-400">En attente...</span>';
                    }
                })
                .catch(() => {
                    document.getElementById('status').innerHTML = '❌ <span class="text-red-400">Erreur</span>';
                });
        }
        setInterval(updateDisplay, 1000);
        updateDisplay();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        if sys.version_info[0] >= 3:
            self.wfile.write(html_part1.encode('utf-8'))
        else:
            self.wfile.write(html_part1)
    
    def serve_mobile_page(self):
        # Marquer comme connecté
        vitals['last_mobile_ping'] = time.time()
        vitals['mobile_connected'] = True
        
        html = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 Contrôle Mobile</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen">
    <div class="container mx-auto p-4 max-w-md">
        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold">📱 Contrôle Scope</h1>
            <div id="status" class="text-green-400 mt-2">✅ Connecté</div>
        </div>
        
        <div class="space-y-4">
            <div class="bg-slate-800 rounded-lg p-4">
                <h3 class="text-green-400 text-lg font-semibold mb-3">💚 FC (bpm)</h3>
                <div class="grid grid-cols-2 gap-4 mb-3">
                    <div><label class="text-xs text-slate-400">Actuelle</label><div id="fc-current" class="text-xl text-green-400">75</div></div>
                    <div><label class="text-xs text-slate-400">Cible</label><div id="fc-target" class="text-xl text-green-400">75</div></div>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="fc-input" min="0" max="300" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" placeholder="0-300">
                    <button onclick="updateFC()" class="bg-green-600 px-4 py-2 rounded">✓</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-4">
                <h3 class="text-cyan-400 text-lg font-semibold mb-3">💙 SpO₂ (%)</h3>
                <div class="grid grid-cols-2 gap-4 mb-3">
                    <div><label class="text-xs text-slate-400">Actuelle</label><div id="spo2-current" class="text-xl text-cyan-400">98</div></div>
                    <div><label class="text-xs text-slate-400">Cible</label><div id="spo2-target" class="text-xl text-cyan-400">98</div></div>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="spo2-input" min="0" max="100" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" placeholder="0-100">
                    <button onclick="updateSpO2()" class="bg-cyan-600 px-4 py-2 rounded">✓</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-4">
                <h3 class="text-yellow-300 text-lg font-semibold mb-3">💛 FR (/min)</h3>
                <div class="grid grid-cols-2 gap-4 mb-3">
                    <div><label class="text-xs text-slate-400">Actuelle</label><div id="fr-current" class="text-xl text-yellow-300">16</div></div>
                    <div><label class="text-xs text-slate-400">Cible</label><div id="fr-target" class="text-xl text-yellow-300">16</div></div>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="fr-input" min="0" max="60" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" placeholder="0-60">
                    <button onclick="updateFR()" class="bg-yellow-600 px-4 py-2 rounded">✓</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-4">
                <div class="flex space-x-2">
                    <button onclick="reset()" class="flex-1 bg-red-600 px-4 py-2 rounded">🔄 Reset</button>
                    <button onclick="emergency()" class="flex-1 bg-orange-600 px-4 py-2 rounded">🚨 Urgence</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function updateDisplay() {
            fetch('/api/vitals')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('fc-current').textContent = data.current.fc;
                    document.getElementById('fc-target').textContent = data.target.fc;
                    document.getElementById('spo2-current').textContent = data.current.spo2;
                    document.getElementById('spo2-target').textContent = data.target.spo2;
                    document.getElementById('fr-current').textContent = data.current.fr;
                    document.getElementById('fr-target').textContent = data.target.fr;
                });
        }
        
        function sendUpdate(data) {
            fetch('/api/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
        }
        
        function updateFC() {
            const val = parseInt(document.getElementById('fc-input').value);
            if (val >= 0 && val <= 300) {
                sendUpdate({fc: val});
                document.getElementById('fc-input').value = '';
            }
        }
        
        function updateSpO2() {
            const val = parseInt(document.getElementById('spo2-input').value);
            if (val >= 0 && val <= 100) {
                sendUpdate({spo2: val});
                document.getElementById('spo2-input').value = '';
            }
        }
        
        function updateFR() {
            const val = parseInt(document.getElementById('fr-input').value);
            if (val >= 0 && val <= 60) {
                sendUpdate({fr: val});
                document.getElementById('fr-input').value = '';
            }
        }
        
        function reset() { sendUpdate({fc: 75, spo2: 98, fr: 16}); }
        function emergency() { sendUpdate({fc: 0, spo2: 0, fr: 0}); }
        
        setInterval(updateDisplay, 1000);
        updateDisplay();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        if sys.version_info[0] >= 3:
            self.wfile.write(html.encode('utf-8'))
        else:
            self.wfile.write(html)
    
    def log_message(self, format, *args):
        pass  # Supprimer les logs HTTP

def transition_worker():
    """Thread pour les transitions réalistes"""
    while True:
        time.sleep(1)
        current = vitals['current']
        target = vitals['target']
        
        # FC: ±2/s
        if current['fc'] != target['fc']:
            diff = target['fc'] - current['fc']
            step = min(abs(diff), 2) * (1 if diff > 0 else -1)
            current['fc'] += step
        
        # SpO2: ±1/s  
        if current['spo2'] != target['spo2']:
            diff = target['spo2'] - current['spo2']
            step = min(abs(diff), 1) * (1 if diff > 0 else -1)
            current['spo2'] += step
        
        # FR: ±1/s
        if current['fr'] != target['fr']:
            diff = target['fr'] - current['fr']
            step = min(abs(diff), 1) * (1 if diff > 0 else -1)
            current['fr'] += step

if __name__ == "__main__":
    print("🎯 Simulateur de Scope Medical v2.0")
    print("=====================================")
    
    # Trouver port libre
    while PORT < 3100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', PORT))
                break
        except OSError:
            PORT += 1
    
    local_ip = get_local_ip()
    print("📺 Interface scope: http://{}:{}".format(local_ip, PORT))
    print("📱 Mobile: http://{}:{}/mobile".format(local_ip, PORT))
    print()
    
    # Démarrer thread transitions
    t = threading.Thread(target=transition_worker)
    t.daemon = True
    t.start()
    
    # Ouvrir navigateur
    try:
        webbrowser.open("http://{}:{}".format(local_ip, PORT))
    except:
        pass
    
    print("✅ Serveur actif - Ctrl+C pour arrêter")
    
    try:
        httpd = socketserver.TCPServer(("", PORT), ScopeHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
        httpd.shutdown()