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
httpd = None  # Variable globale pour le serveur

# État des signes vitaux
vitals = {
    'current': {'fc': 140, 'spo2': 98, 'fr': 50},
    'target': {'fc': 140, 'spo2': 98, 'fr': 50},
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
        elif path == '/api/shutdown':
            self.serve_shutdown()
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
                
                print("Mise a jour: FC={}, SpO2={}, FR={}".format(
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

    def serve_shutdown(self):
        # Endpoint pour fermer le serveur
        self.send_json({'message': 'Serveur en cours d\'arret...'})
        # Arrêter le serveur dans un thread séparé
        import threading
        def shutdown():
            time.sleep(0.5)  # Laisser le temps de répondre
            try:
                global httpd
                httpd.shutdown()
            except:
                import os
                os._exit(0)
        threading.Thread(target=shutdown).start()
    
    def serve_scope_page(self):
        local_ip = get_local_ip()
        mobile_url = "http://{}:{}/mobile".format(local_ip, PORT)
        
        # HTML sans problème de formatage
        html_part1 = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Simulateur de Scope Médical</title>
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
        <div class="flex items-center gap-2">
            <span>Mobile: <a href="''' + mobile_url + '''" class="text-blue-400 underline">''' + mobile_url + '''</a></span>
            <button onclick="showQRCode()" class="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-white text-xs flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM13 13h2v2h-2v-2zM15 15h2v2h-2v-2zM13 17h2v2h-2v-2zM15 19h2v2h-2v-2zM17 13h2v2h-2v-2zM19 15h2v2h-2v-2zM17 17h2v2h-2v-2zM19 19h2v2h-2v-2z"/>
                </svg>
                QR
            </button>
        </div>
    </div>

    <!-- Modal QR Code -->
    <div id="qr-modal" class="fixed inset-0 bg-black bg-opacity-75 hidden flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div class="text-center">
                <h3 class="text-lg font-bold text-black mb-4">Scanner pour accéder au contrôle mobile</h3>
                <div id="qr-code" class="flex justify-center mb-4"></div>
                <button onclick="hideQRCode()" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded">Fermer</button>
            </div>
        </div>
    </div>

    <!-- Toaster de notification -->
    <div id="toast" class="fixed top-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg transition-transform duration-300 z-50" style="right: -400px;">
        <div class="flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span id="toast-message">Mobile connecté !</span>
        </div>
    </div>
    
    <div class="h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-6xl h-[700px] bg-black rounded-lg border-2 border-slate-700 grid grid-cols-[3fr,1fr] gap-2 p-2">
            
            <div class="grid grid-rows-3 gap-1">
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-green-400 text-sm mb-1">ECG (FC)</div><canvas id="ecg-canvas" width="800" height="120" class="w-full bg-black rounded" style="height: 80%"></canvas></div>
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-cyan-400 text-sm mb-1">Pleth (SpO₂)</div><canvas id="pleth-canvas" width="800" height="120" class="w-full bg-black rounded" style="height: 80%"></canvas></div>
                <div class="bg-slate-800 rounded p-2 waveform"><div class="text-yellow-300 text-sm mb-1">Resp (FR)</div><canvas id="resp-canvas" width="800" height="120" class="w-full bg-black rounded" style="height: 80%"></canvas></div>
            </div>
            
            <div class="bg-slate-800 rounded p-4 flex flex-col justify-around">
                <div class="flex items-center justify-between py-6">
                    <div class="flex items-center">
                        <div><span class="text-green-400 font-bold text-2xl">FC</span><span class="text-lg text-green-400 opacity-80 ml-3">bpm</span></div>
                    </div>
                    <div id="fc-display" class="text-7xl font-bold text-green-400 vital-display">140</div>
                </div>
                
                <div class="flex items-center justify-between py-6">
                    <div class="flex items-center">
                        <div><span class="text-cyan-400 font-bold text-2xl">SpO₂</span><span class="text-lg text-cyan-400 opacity-80 ml-3">%</span></div>
                    </div>
                    <div id="spo2-display" class="text-7xl font-bold text-cyan-400 vital-display">98</div>
                </div>
                
                <div class="flex items-center justify-between py-6">
                    <div class="flex items-center">
                        <div><span class="text-yellow-300 font-bold text-2xl">FR</span><span class="text-lg text-yellow-300 opacity-80 ml-3">/min</span></div>
                    </div>
                    <div id="fr-display" class="text-7xl font-bold text-yellow-300 vital-display">50</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Configuration du balayage scope réaliste
        const SAMPLES_PER_SECOND = 50;
        const UPDATE_INTERVAL_MS = 1000 / SAMPLES_PER_SECOND; // 20ms
        const CANVAS_WIDTH = 800;
        const SWEEP_SPEED = 2; // pixels par frame
        const ERASE_WIDTH = 20; // largeur de la zone d'effacement
        
        // Buffers de données pour chaque courbe (index = position X sur le canvas)
        let ecgBuffer = new Array(CANVAS_WIDTH).fill(null);
        let plethBuffer = new Array(CANVAS_WIDTH).fill(null);
        let respBuffer = new Array(CANVAS_WIDTH).fill(null);
        
        // Position actuelle du balayage (de 0 à CANVAS_WIDTH puis revient à 0)
        let sweepPosition = 0;
        
        // Pattern ECG réaliste (identique à la version TSX)
        const NORMAL_SINUS_PATTERN_BASE = [
            0, 0.05, 0.1, // P wave
            0.05, 0, -0.1, // PR segment
            0.5, 1.2, -0.4, 0.2, // QRS complex
            0, 0.1, 0.2, 0.3, 0.25, // T wave
            0.15, 0 // End of T wave
        ];
        
        const PLETH_NORMAL_PATTERN_BASE = [
            0.1, 0.2, 0.5, 0.9, 1.0, // Anacrotic limb to peak
            0.8, 0.65, 0.7, // Dicrotic notch
            0.5, 0.3, 0.15, 0.1 // Dicrotic limb to baseline
        ];
        
        const RESP_NORMAL_PATTERN_BASE = [
            0, 0.15, 0.3, 0.4, 0.5, // Inspiration
            0.4, 0.3, 0.15, 0, // Expiration start
            -0.15, -0.3, -0.4, -0.5, // Expiration deeper
            -0.4, -0.3, -0.15, 0 // Return to baseline
        ];
        
        // Fonction pour créer un pattern interpolé
        function createPattern(base, targetLengthFraction) {
            const targetLength = Math.max(5, Math.floor(SAMPLES_PER_SECOND * targetLengthFraction));
            if (base.length === 0) return Array(targetLength).fill(0);
            
            const result = [];
            for (let i = 0; i < targetLength; i++) {
                const baseIndex = (i / (targetLength - 1)) * (base.length - 1);
                const idx1 = Math.floor(baseIndex);
                const idx2 = Math.min(idx1 + 1, base.length - 1);
                const frac = baseIndex - idx1;
                result.push(base[idx1] * (1 - frac) + base[idx2] * frac);
            }
            return result;
        }
        
        const ecgPattern = createPattern(NORMAL_SINUS_PATTERN_BASE, 0.7);
        const plethPattern = createPattern(PLETH_NORMAL_PATTERN_BASE, 0.7);
        const respPattern = createPattern(RESP_NORMAL_PATTERN_BASE, 3.0);
        
        // Variables pour le cycle de patterns
        let ecgCycleProgress = 0;
        let plethCycleProgress = 0;
        let respCycleProgress = 0;
        let ecgCurrentCycleSamples = 0;
        let plethCurrentCycleSamples = 0;
        let respCurrentCycleSamples = 0;
        
        function drawScopeWaveform(canvasId, buffer, color, yDomain) {
            const canvas = document.getElementById(canvasId);
            const ctx = canvas.getContext('2d');
            
            // Effacer le canvas complètement
            ctx.fillStyle = '#000000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Grille de fond
            ctx.strokeStyle = '#374151';
            ctx.lineWidth = 0.5;
            for (let x = 0; x < canvas.width; x += 20) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 20) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
            
            // Dessiner la courbe - approche simplifiée qui marche
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            let hasStarted = false;
            let lastValidX = -1;
            
            for (let x = 0; x < buffer.length; x++) {
                if (buffer[x] !== null) {
                    const normalizedY = (buffer[x] - yDomain[0]) / (yDomain[1] - yDomain[0]);
                    const y = canvas.height * (1 - normalizedY);
                    
                    if (!hasStarted) {
                        ctx.moveTo(x, y);
                        hasStarted = true;
                    } else {
                        // Si il y a plus de 5 pixels de gap, commencer un nouveau segment
                        if (x - lastValidX > 5) {
                            ctx.stroke();
                            ctx.beginPath();
                            ctx.moveTo(x, y);
                        } else {
                            ctx.lineTo(x, y);
                        }
                    }
                    lastValidX = x;
                }
            }
            
            if (hasStarted) {
                ctx.stroke();
            }
        }
        
        function generateNextPoint(pattern, cycleProgress, currentCycleSamples, targetRate, yDomain, valueType) {
            if (targetRate === 0 || !pattern || pattern.length === 0) {
                // Pour les cas d'arrêt (FC=0, FR=0), ligne plate
                const flatValue = valueType === 'ecg' ? 0 : (yDomain[0] + yDomain[1]) / 2;
                return { value: flatValue, newProgress: 0, newCycleSamples: 0 };
            }
            
            if (currentCycleSamples === 0) {
                const baseSamplesPerCycle = (60 / targetRate) * SAMPLES_PER_SECOND;
                const periodVariationFactor = 1 + (Math.random() - 0.5) * 0.10;
                currentCycleSamples = Math.max(SAMPLES_PER_SECOND / 10, baseSamplesPerCycle * periodVariationFactor);
            }
            
            const patternIndexFloat = (cycleProgress / currentCycleSamples) * pattern.length;
            const patternIndex = Math.floor(patternIndexFloat) % pattern.length;
            
            let value = pattern[patternIndex];
            
            // Ajustements spécifiques selon le type et les valeurs
            if (valueType === 'ecg') {
                // Amplitude varie selon la FC - plus rapide = moins d'amplitude
                const fcFactor = Math.max(0.3, Math.min(1.2, 100 / Math.max(targetRate, 30)));
                value *= fcFactor;
            } else if (valueType === 'pleth') {
                // Amplitude varie selon SpO2
                const spo2Factor = vitals.current.spo2 / 100;
                value *= spo2Factor;
            }
            
            // Variation d'amplitude naturelle
            const amplitudeVariationFactor = 1 + (Math.random() - 0.5) * 0.10;
            value *= amplitudeVariationFactor;
            
            cycleProgress += 1;
            
            if (cycleProgress >= currentCycleSamples) {
                cycleProgress = 0;
                // Recalculer les samples avec la nouvelle fréquence
                const baseSamplesPerCycle = (60 / targetRate) * SAMPLES_PER_SECOND;
                const periodVariationFactor = 1 + (Math.random() - 0.5) * 0.10;
                currentCycleSamples = Math.max(SAMPLES_PER_SECOND / 10, baseSamplesPerCycle * periodVariationFactor);
            }
            
            // Clamp value to yDomain
            value = Math.max(yDomain[0], Math.min(yDomain[1], value));
            
            return { value, newProgress: cycleProgress, newCycleSamples: currentCycleSamples };
        }
        
        // Variables pour détecter les changements de valeurs
        let lastFC = 140;
        let lastSpO2 = 98;
        let lastFR = 50;
        
        function updateWaveforms() {
            // Détecter les changements de valeurs et réinitialiser les cycles si nécessaire
            if (vitals.current.fc !== lastFC) {
                ecgCycleProgress = 0;
                ecgCurrentCycleSamples = 0;
                lastFC = vitals.current.fc;
            }
            
            if (vitals.current.spo2 !== lastSpO2) {
                plethCycleProgress = 0;
                plethCurrentCycleSamples = 0;
                lastSpO2 = vitals.current.spo2;
            }
            
            if (vitals.current.fr !== lastFR) {
                respCycleProgress = 0;
                respCurrentCycleSamples = 0;
                lastFR = vitals.current.fr;
            }
            
            // Calculer la position d'écriture actuelle
            const writePosition = Math.floor(sweepPosition) % CANVAS_WIDTH;
            
            // Générer et écrire le nouveau point à la position de balayage
            const ecgResult = generateNextPoint(ecgPattern, ecgCycleProgress, ecgCurrentCycleSamples, vitals.current.fc, [-1.5, 2], 'ecg');
            ecgCycleProgress = ecgResult.newProgress;
            ecgCurrentCycleSamples = ecgResult.newCycleSamples;
            ecgBuffer[writePosition] = ecgResult.value;
            
            const plethResult = generateNextPoint(plethPattern, plethCycleProgress, plethCurrentCycleSamples, vitals.current.spo2 > 0 ? 60 : 0, [-0.2, 1.2], 'pleth');
            plethCycleProgress = plethResult.newProgress;
            plethCurrentCycleSamples = plethResult.newCycleSamples;
            plethBuffer[writePosition] = plethResult.value;
            
            const respResult = generateNextPoint(respPattern, respCycleProgress, respCurrentCycleSamples, vitals.current.fr, [-0.6, 0.6], 'resp');
            respCycleProgress = respResult.newProgress;
            respCurrentCycleSamples = respResult.newCycleSamples;
            respBuffer[writePosition] = respResult.value;
            
            // DEBUG - Log pour voir ce qui se passe
            if (Math.floor(sweepPosition) % 50 === 0) {
                console.log('Position:', writePosition, 'ECG:', ecgResult.value, 'FC:', vitals.current.fc);
                console.log('Buffer sample:', ecgBuffer.slice(writePosition-5, writePosition+5));
            }
            
            // Effacer la zone de balayage APRÈS avoir écrit le nouveau point (créer l'espace vide)
            for (let i = 1; i < ERASE_WIDTH; i++) {
                const pos = (writePosition + i) % CANVAS_WIDTH;
                ecgBuffer[pos] = null;
                plethBuffer[pos] = null;
                respBuffer[pos] = null;
            }
            
            // Avancer la position de balayage
            sweepPosition += SWEEP_SPEED;
            if (sweepPosition >= CANVAS_WIDTH) {
                sweepPosition = 0; // Revenir au début
            }
            
            // Dessiner les courbes avec le système de balayage
            drawScopeWaveform('ecg-canvas', ecgBuffer, '#10b981', [-1.5, 2]);
            drawScopeWaveform('pleth-canvas', plethBuffer, '#06b6d4', [-0.2, 1.2]);
            drawScopeWaveform('resp-canvas', respBuffer, '#eab308', [-0.6, 0.6]);
        }
        
        let vitals = {current: {fc: 140, spo2: 98, fr: 50}};
        let wasMobileConnected = false; // Pour détecter le changement de statut

        function updateDisplay() {
            fetch('/api/vitals')
                .then(r => r.json())
                .then(data => {
                    vitals = data;
                    
                    // Ajouter oscillations ±1 sur l'affichage (sauf si valeur = 0)
                    const fcOscillation = data.current.fc === 0 ? 0 : Math.round((Math.random() - 0.5) * 2); // -1, 0, ou +1
                    const spo2Oscillation = data.current.spo2 === 0 ? 0 : Math.round((Math.random() - 0.5) * 2);
                    const frOscillation = data.current.fr === 0 ? 0 : Math.round((Math.random() - 0.5) * 2);

                    document.getElementById('fc-display').textContent = Math.max(0, data.current.fc + fcOscillation);
                    document.getElementById('spo2-display').textContent = Math.max(0, Math.min(100, data.current.spo2 + spo2Oscillation));
                    document.getElementById('fr-display').textContent = Math.max(0, data.current.fr + frOscillation);
                    
                    // Détecter nouvelle connexion mobile
                    if (data.mobile_connected && !wasMobileConnected) {
                        wasMobileConnected = true;
                        hideQRCode(); // Fermer le modal QR
                        showToast('Mobile connecté !'); // Afficher toaster
                    } else if (!data.mobile_connected) {
                        wasMobileConnected = false;
                    }
                })
                .catch(() => {
                    // Erreur de connexion - pas d'affichage nécessaire
                });
        }

        // Fonctions QR Code
        function showQRCode() {
            const modal = document.getElementById('qr-modal');
            const qrContainer = document.getElementById('qr-code');
            const mobileUrl = window.location.origin + '/mobile';

            // Vider le container
            qrContainer.innerHTML = '';

            // Générer QR code avec une API publique
            const qrImg = document.createElement('img');
            qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(mobileUrl)}`;
            qrImg.alt = 'QR Code';
            qrImg.className = 'mx-auto';
            qrContainer.appendChild(qrImg);

            modal.classList.remove('hidden');
        }

        function hideQRCode() {
            document.getElementById('qr-modal').classList.add('hidden');
        }

        // Fermer modal en cliquant à l'extérieur
        document.getElementById('qr-modal').addEventListener('click', function(e) {
            if (e.target === this) {
                hideQRCode();
            }
        });

        // Fonction toaster
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            const messageElement = document.getElementById('toast-message');

            messageElement.textContent = message;

            // Couleurs selon le type
            if (type === 'success') {
                toast.className = toast.className.replace(/bg-\w+-600/g, 'bg-green-600');
            } else if (type === 'error') {
                toast.className = toast.className.replace(/bg-\w+-600/g, 'bg-red-600');
            }

            // Afficher le toast (slide in)
            toast.style.right = '16px';

            // Masquer après 3 secondes (slide out)
            setTimeout(() => {
                toast.style.right = '-400px';
            }, 3000);
        }

        // Détecter fermeture de page et arrêter le serveur
        window.addEventListener('beforeunload', function(e) {
            // Envoyer requête pour arrêter le serveur
            fetch('/api/shutdown', {method: 'GET'}).catch(() => {});
        });

        window.addEventListener('unload', function(e) {
            // Backup au cas où beforeunload ne marche pas
            fetch('/api/shutdown', {method: 'GET'}).catch(() => {});
        });

        // Démarrer les animations
        setInterval(updateDisplay, 1000);
        setInterval(updateWaveforms, UPDATE_INTERVAL_MS); // 50 FPS comme la version TSX (20ms)
        updateDisplay();
        updateWaveforms();
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
    <title>Contrôle Mobile</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen">
    <div class="container mx-auto p-4 max-w-md">
        <div class="text-center mb-6">
            <h1 class="text-2xl font-bold">Contrôle Scope</h1>
            <div id="status" class="text-green-400 mt-2">Connecté</div>
        </div>
        
        <div class="space-y-3">
            <div class="bg-slate-800 rounded-lg p-3">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-green-400 text-lg font-semibold">FC (bpm)</h3>
                    <div class="flex space-x-4">
                        <div class="text-center"><label class="text-xs text-slate-400">Actuelle</label><div id="fc-current" class="text-lg text-green-400 font-bold">140</div></div>
                        <div class="text-center"><label class="text-xs text-slate-400">Cible</label><div id="fc-target" class="text-lg text-green-400 font-bold">140</div></div>
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({fc: 50})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">50</button>
                    <button onclick="sendUpdate({fc: 70})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">70</button>
                    <button onclick="sendUpdate({fc: 80})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">80</button>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({fc: 90})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">90</button>
                    <button onclick="sendUpdate({fc: 110})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">110</button>
                    <button onclick="sendUpdate({fc: 130})" class="bg-green-700 hover:bg-green-600 text-white py-1 rounded text-sm font-medium">130</button>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="fc-input" min="0" max="300" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" onkeypress="if(event.key==='Enter')updateFC()">
                    <button onclick="updateFC()" class="bg-green-600 px-4 py-2 rounded font-bold">OK</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-3">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-cyan-400 text-lg font-semibold">SpO₂ (%)</h3>
                    <div class="flex space-x-4">
                        <div class="text-center"><label class="text-xs text-slate-400">Actuelle</label><div id="spo2-current" class="text-lg text-cyan-400 font-bold">98</div></div>
                        <div class="text-center"><label class="text-xs text-slate-400">Cible</label><div id="spo2-target" class="text-lg text-cyan-400 font-bold">98</div></div>
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({spo2: 55})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">55</button>
                    <button onclick="sendUpdate({spo2: 65})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">65</button>
                    <button onclick="sendUpdate({spo2: 75})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">75</button>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({spo2: 86})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">86</button>
                    <button onclick="sendUpdate({spo2: 95})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">95</button>
                    <button onclick="sendUpdate({spo2: 100})" class="bg-cyan-700 hover:bg-cyan-600 text-white py-1 rounded text-sm font-medium">100</button>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="spo2-input" min="0" max="100" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" onkeypress="if(event.key==='Enter')updateSpO2()">
                    <button onclick="updateSpO2()" class="bg-cyan-600 px-4 py-2 rounded font-bold">OK</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-3">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-yellow-300 text-lg font-semibold">FR (/min)</h3>
                    <div class="flex space-x-4">
                        <div class="text-center"><label class="text-xs text-slate-400">Actuelle</label><div id="fr-current" class="text-lg text-yellow-300 font-bold">50</div></div>
                        <div class="text-center"><label class="text-xs text-slate-400">Cible</label><div id="fr-target" class="text-lg text-yellow-300 font-bold">50</div></div>
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({fr: 0})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">0</button>
                    <button onclick="sendUpdate({fr: 20})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">20</button>
                    <button onclick="sendUpdate({fr: 30})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">30</button>
                </div>
                <div class="grid grid-cols-3 gap-1 mb-2">
                    <button onclick="sendUpdate({fr: 40})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">40</button>
                    <button onclick="sendUpdate({fr: 50})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">50</button>
                    <button onclick="sendUpdate({fr: 60})" class="bg-yellow-700 hover:bg-yellow-600 text-white py-1 rounded text-sm font-medium">60</button>
                </div>
                <div class="flex space-x-2">
                    <input type="number" id="fr-input" min="0" max="60" class="flex-1 bg-slate-700 text-white px-3 py-2 rounded" onkeypress="if(event.key==='Enter')updateFR()">
                    <button onclick="updateFR()" class="bg-yellow-600 px-4 py-2 rounded font-bold">OK</button>
                </div>
            </div>
            
            <div class="bg-slate-800 rounded-lg p-3">
                <button onclick="reset()" class="w-full bg-red-600 px-4 py-2 rounded font-bold">Reset (140 - 98 - 50)</button>
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

                    // Mise à jour des placeholders avec les valeurs actuelles
                    const fcInput = document.getElementById('fc-input');
                    const spo2Input = document.getElementById('spo2-input');
                    const frInput = document.getElementById('fr-input');

                    if (fcInput) fcInput.placeholder = data.target.fc + ' bpm';
                    if (spo2Input) spo2Input.placeholder = data.target.spo2 + '%';
                    if (frInput) frInput.placeholder = data.target.fr + ' /min';
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
                document.getElementById('fc-input').blur(); // Fermer le clavier
            }
        }
        
        function updateSpO2() {
            const val = parseInt(document.getElementById('spo2-input').value);
            if (val >= 0 && val <= 100) {
                sendUpdate({spo2: val});
                document.getElementById('spo2-input').value = '';
                document.getElementById('spo2-input').blur(); // Fermer le clavier
            }
        }
        
        function updateFR() {
            const val = parseInt(document.getElementById('fr-input').value);
            if (val >= 0 && val <= 60) {
                sendUpdate({fr: val});
                document.getElementById('fr-input').value = '';
                document.getElementById('fr-input').blur(); // Fermer le clavier
            }
        }
        
        function reset() { sendUpdate({fc: 140, spo2: 98, fr: 50}); }
        
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
    """Thread pour les transitions proportionnelles"""
    while True:
        time.sleep(0.1)  # Vérification rapide (10x par seconde)
        current = vitals['current']
        target = vitals['target']
        
        # FC: Transition en 10 secondes
        if current['fc'] != target['fc']:
            diff = target['fc'] - current['fc']
            # Pour atteindre la cible en 10 secondes avec 100 étapes (10x/s * 10s)
            step = diff / 100.0
            if abs(step) < 1:
                step = 1 if diff > 0 else -1
            current['fc'] = int(min(max(0, current['fc'] + step), 300))
        
        # SpO2: Transition en 10 secondes
        if current['spo2'] != target['spo2']:
            diff = target['spo2'] - current['spo2']
            step = diff / 100.0
            if abs(step) < 1:
                step = 1 if diff > 0 else -1
            current['spo2'] = int(min(max(0, current['spo2'] + step), 100))
        
        # FR: Transition en 10 secondes
        if current['fr'] != target['fr']:
            diff = target['fr'] - current['fr']
            step = diff / 100.0
            if abs(step) < 1:
                step = 1 if diff > 0 else -1
            current['fr'] = int(min(max(0, current['fr'] + step), 60))

def start_server():
    global httpd, PORT
    print("Simulateur de Scope Medical v2.0")
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
    print("Interface scope: http://{}:{}".format(local_ip, PORT))
    print("Mobile: http://{}:{}/mobile".format(local_ip, PORT))
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
    
    print("Serveur actif - Ctrl+C pour arreter")

    try:
        httpd = socketserver.TCPServer(("", PORT), ScopeHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArret du serveur")
        if httpd:
            httpd.shutdown()

if __name__ == "__main__":
    start_server()