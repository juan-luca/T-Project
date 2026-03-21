# CyberCommandCenter - Documentación Funcional para IA

## Descripción General
CyberCommandCenter es una plataforma integral de ciberseguridad que permite la gestión, monitoreo y control de dispositivos y redes desde una interfaz centralizada. El sistema está dividido en un backend (Python/Flask) y un frontend (React), permitiendo la interacción entre usuarios y herramientas de ciberseguridad avanzadas.

## Estructura del Proyecto
- **backend/**: Lógica de negocio, APIs, gestión de dispositivos, auditoría WiFi, control parental, ataques de red, monitorización de tráfico, integración con Telegram, y más.
- **frontend/**: Interfaz de usuario desarrollada en React, con páginas para cada funcionalidad principal (Dashboard, Control de Dispositivos, Auditoría WiFi, Pranks, Seguridad, etc.).

## Funcionalidades Principales
1. **Auditoría y Hacking WiFi**: Permite analizar redes WiFi, detectar vulnerabilidades y realizar pruebas de penetración controladas.
2. **Control de Dispositivos**: Gestión y control de dispositivos conectados a la red, incluyendo perfiles y restricciones.
3. **Monitorización de Tráfico**: Captura y análisis de paquetes de red en tiempo real, con alertas configurables.
4. **Pranks y Network Pranks**: Herramientas para realizar bromas en la red (ej. deauth, ARP spoofing, etc.) de forma controlada.
5. **Control Parental**: Restricción de acceso a dispositivos o servicios según reglas definidas.
6. **Gestión de Alertas**: Sistema de alertas ante eventos sospechosos o configurados por el usuario.
7. **Integración con Telegram**: Notificaciones y control remoto a través de un bot de Telegram.
8. **Gestión de Temas y Configuración**: Personalización de la interfaz y parámetros del sistema.

## Backend (Python/Flask)
- **app.py**: Punto de entrada de la API Flask.
- **core/**: Módulos funcionales (sniffer, deauth, parental, pranks, scheduler, logger, etc.).
- **api/**: Rutas de la API REST (ej. wifi_audit_routes.py).
- **database/**: Modelos y gestión de la base de datos.
- **config.py**: Configuración global del backend.

## Frontend (React)
- **src/pages/**: Cada página representa una funcionalidad principal.
- **src/components/**: Componentes reutilizables (Header, Sidebar, ErrorBoundary).
- **src/services/api.js**: Comunicación con el backend.

## Flujo Funcional
1. El usuario accede al frontend y selecciona una herramienta o funcionalidad.
2. El frontend realiza peticiones a la API del backend.
3. El backend ejecuta la lógica correspondiente (ej. escaneo WiFi, control de dispositivos, prank, etc.) y responde al frontend.
4. El frontend muestra los resultados y permite nuevas acciones.
5. El sistema puede enviar notificaciones a Telegram según la configuración.

## Consideraciones para IA
- Cada funcionalidad está modularizada en el backend.
- La comunicación entre frontend y backend es vía API REST.
- El sistema es extensible: se pueden agregar nuevas herramientas en `core/` y exponerlas vía `api/`.
- El frontend consume los endpoints y muestra la información de forma amigable.
- Los scripts batch (`start.bat`, `stop.bat`, `install.bat`) permiten gestionar el ciclo de vida del sistema.

## Ejemplo de Uso
- Un usuario quiere auditar su red WiFi: accede a la página WiFiAudit, inicia un escaneo, el backend procesa la solicitud y devuelve los resultados, que se muestran en el frontend.

## Requisitos
- Python 3.x y dependencias de `requirements.txt` para el backend.
- Node.js y dependencias de `package.json` para el frontend.

---

Esta documentación permite a una IA comprender la arquitectura, flujo y funcionalidades del sistema para poder operar, modificar o ampliar el proyecto sin necesidad de inspeccionar los archivos fuente directamente.