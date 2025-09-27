# Control de Pantalla por Gestos

![Captura de uso de amazonQ](Captura%20de%20pantalla_20250926_232801.png)

## Descripción del Proyecto

Una aplicación de visión por computadora que permite controlar la pantalla a través de gestos de mano usando entrada de cámara en tiempo real. El sistema utiliza MediaPipe para detección y seguimiento preciso de manos, proporcionando una interfaz intuitiva para interacción basada en gestos.

## Características Principales

- **Detección de Manos en Tiempo Real**: Utiliza algoritmos avanzados de seguimiento de manos de MediaPipe para detección precisa de puntos de referencia
- **Procesamiento de Video en Vivo**: Captura y procesa el feed de video desde la cámara predeterminada (webcam)
- **Retroalimentación Visual**: Muestra puntos de referencia y conexiones de las manos superpuestos en el flujo de video
- **Reconocimiento de Gestos**: Implementa tres gestos principales para control de pantalla

## Gestos Soportados

### 🖱️ Gesto L (Mover Mouse)
- **Descripción**: Índice y pulgar extendidos, otros dedos cerrados
- **Función**: Controla el movimiento del cursor del mouse

### 👆 Gesto de Apuntar (Click)
- **Descripción**: Solo índice arriba, pulgar cerrado
- **Función**: Realiza click izquierdo del mouse

### ✌️ Dos Dedos (Scroll)
- **Descripción**: Índice y medio arriba
- **Función**: Scroll vertical en la pantalla

## Instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd "control de pantalla por gestos"
```

2. Crea un entorno virtual:
```bash
python -m venv venv310
source venv310/bin/activate  # En Linux/Mac
# o
venv310\Scripts\activate  # En Windows
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación:
```bash
python gestos.py
```

### Controles:
- Presiona 'q' para salir (cuando la cámara está visible)
- El sistema funciona en segundo plano cuando la cámara está oculta

## Usuarios Objetivo

- **Desarrolladores**: Construyendo aplicaciones e interfaces controladas por gestos
- **Usuarios de Accesibilidad**: Buscando métodos alternativos de entrada para interacción con computadora
- **Diseñadores de Sistemas Interactivos**: Creando sistemas de control sin contacto
- **Entusiastas de Visión por Computadora**: Aprendiendo seguimiento de manos y reconocimiento de gestos

## Casos de Uso

- Control de computadora sin contacto para entornos sensibles a la higiene
- Soluciones de accesibilidad para usuarios con movilidad limitada
- Presentaciones y demostraciones interactivas
- Aplicaciones de juegos y entretenimiento
- Control de dispositivos domésticos inteligentes a través de gestos
- Herramientas educativas para aprendizaje de visión por computadora

## Propuesta de Valor

Proporciona una base para construir interfaces sofisticadas controladas por gestos combinando detección robusta de manos con procesamiento de video en tiempo real, permitiendo interacción humano-computadora natural e intuitiva sin contacto físico.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal
- **OpenCV**: Procesamiento de video y visión por computadora
- **MediaPipe**: Detección y seguimiento de manos
- **PyAutoGUI**: Control del mouse y teclado del sistema

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para mejoras.

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.