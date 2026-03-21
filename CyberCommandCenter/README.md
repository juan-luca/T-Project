# 🛡️ Cyber Command Center

<div align="center">

![Cyber Command Center](https://img.shields.io/badge/Cyber-Command%20Center-00f0ff?style=for-the-badge&logo=shield&logoColor=white)

**Dashboard de Ciberseguridad para Red Doméstica**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat-square&logo=react)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com)

</div>

---

## ⚠️ AVISO LEGAL IMPORTANTE

Este software está diseñado **EXCLUSIVAMENTE** para:
- Uso educativo y de aprendizaje
- Pruebas en tu **PROPIA** red doméstica
- Entornos de laboratorio controlados

**NO** uses estas herramientas en redes ajenas sin autorización explícita.
El uso indebido puede ser **ILEGAL** y acarrear consecuencias legales.

---

## 🚀 Características

### 📡 Monitoreo de Red
- Escaneo de dispositivos conectados (ARP, Ping, Nmap)
- Identificación automática de fabricantes
- Detección de nuevos dispositivos en tiempo real
- Historial de conexiones

### 🎭 Pranks (Bromas de Red)
- **Rickroll**: Redirecciona todo el tráfico HTTP a Rick Astley
- **Internet Kill Switch**: Corta temporalmente el acceso a internet
- **Slow Mode**: Reduce el ancho de banda de dispositivos
- **DNS Spoofing**: Redirecciona dominios específicos
- **Fake Popups**: Muestra mensajes personalizados

### 📶 Auditoría WiFi
- Escaneo de redes WiFi cercanas
- Captura de handshakes WPA/WPA2
- Cracking de contraseñas (aircrack-ng, hashcat)
- Ataques WPS
- Ataques de deautenticación

### 🔒 Seguridad
- Escaneo de vulnerabilidades
- Detección de intrusos
- Alertas en tiempo real
- Bloqueo de dispositivos

### 📊 Análisis de Tráfico
- Captura de paquetes en tiempo real
- Análisis de protocolos
- Estadísticas de uso
- Exportación a PCAP

### 🛠️ Herramientas
- Ping
- Traceroute
- DNS Lookup
- Port Scanner
- Wake on LAN

---

## 📋 Requisitos

### Software Base
- **Python** 3.10 o superior
- **Node.js** 18 o superior
- **npm** 9 o superior

### Herramientas Adicionales (Opcionales pero Recomendadas)
- **Npcap** - Para captura de paquetes en Windows
  - Descargar: https://npcap.com/
- **Aircrack-ng** - Para auditoría WiFi
  - Descargar: https://www.aircrack-ng.org/
- **Hashcat** - Para cracking avanzado
  - Descargar: https://hashcat.net/hashcat/

### Adaptador WiFi
Para funciones de auditoría WiFi, necesitas un adaptador que soporte **modo monitor**:
- Alfa AWUS036ACH
- Alfa AWUS036NHA
- TP-Link TL-WN722N (v1)

---

## ⚡ Instalación Rápida

### Windows
```batch
# 1. Clona o descarga el repositorio

# 2. Ejecuta como Administrador:
install.bat

# 3. Inicia el sistema:
start.bat
```

### Manual
```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

---

## 🖥️ Uso

1. **Inicia el sistema** ejecutando `start.bat` como Administrador
2. **Abre el navegador** en http://localhost:5173
3. **Dashboard**: Vista general de tu red
4. **Dispositivos**: Gestiona dispositivos conectados
5. **Pranks**: Ejecuta bromas en dispositivos
6. **WiFi Audit**: Audita redes WiFi cercanas
7. **Seguridad**: Escanea vulnerabilidades
8. **Tráfico**: Analiza paquetes de red
9. **Herramientas**: Utilidades de diagnóstico

---

## 🏗️ Estructura del Proyecto

```
CyberCommandCenter/
├── backend/
│   ├── app.py              # Aplicación Flask principal
│   ├── config.py           # Configuración
│   ├── requirements.txt    # Dependencias Python
│   ├── api/
│   │   └── wifi_audit_routes.py
│   ├── core/
│   │   ├── scanner.py      # Escaneo de red
│   │   ├── arp_spoofer.py  # ARP Spoofing
│   │   ├── deauth.py       # Ataques deauth
│   │   ├── wifi_audit.py   # Auditoría WiFi
│   │   ├── packet_sniffer.py
│   │   └── pranks.py       # Sistema de pranks
│   └── database/
│       └── models.py       # Modelos SQLAlchemy
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   └── Header.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── Devices.jsx
│       │   ├── Pranks.jsx
│       │   ├── WiFiAudit.jsx
│       │   ├── Security.jsx
│       │   ├── Tools.jsx
│       │   ├── Traffic.jsx
│       │   ├── Logs.jsx
│       │   └── Settings.jsx
│       └── services/
│           └── api.js
├── install.bat
├── start.bat
├── stop.bat
└── README.md
```

---

## 🔧 Configuración

### Cambiar Interfaz de Red
Edita `backend/config.py`:
```python
NETWORK_INTERFACE = "wlan0"  # Cambia por tu interfaz
```

### Cambiar Subred
```python
NETWORK_SUBNET = "192.168.1.0/24"
```

---

## 🐛 Solución de Problemas

### "Npcap no encontrado"
- Instala Npcap desde https://npcap.com/
- Marca "Install Npcap in WinPcap API-compatible Mode"

### "No se detectan dispositivos"
- Ejecuta como Administrador
- Verifica que la interfaz de red sea correcta
- Comprueba que estés en la subred correcta

### "Error en captura WiFi"
- Necesitas un adaptador compatible con modo monitor
- Instala aircrack-ng y sus drivers

### "Frontend no carga"
- Verifica que Node.js esté instalado
- Ejecuta `npm install` en la carpeta frontend

---

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea? ¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -am 'Añade nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto es solo para uso educativo. Úsalo responsablemente.

---

<div align="center">

**Hecho con ❤️ para aprender ciberseguridad**

</div>
