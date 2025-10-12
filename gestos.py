#!/usr/bin/env python3
import cv2
import mediapipe as mp
import pyautogui
import math
import argparse
import time

class GestureController:
    def __init__(self, show_camera=False):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            model_complexity=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.show_camera = show_camera
        
        # Variables para control de gestos
        self.prev_y = 0
        self.scroll_sensitivity = 5
        self.last_click_time = 0
        self.click_cooldown = 0.3
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.15
        
        # Suavizado de movimiento mejorado
        self.smooth_factor = 0.85  # Mayor suavizado
        self.prev_mouse_x, self.prev_mouse_y = pyautogui.position()
        self.last_mouse_x, self.last_mouse_y = 0, 0
        
        # Filtro de movimiento mínimo
        self.min_movement = 3  # Píxeles mínimos para mover
        
        # Buffer de posiciones para mayor estabilidad
        self.position_buffer = []
        self.position_buffer_size = 5
        
        # Estabilización de gestos
        self.gesture_buffer = []
        self.buffer_size = 5  # Buffer más grande
        
        # Configurar pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.001

    def get_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def is_finger_up(self, landmarks, finger_tip, finger_pip):
        return landmarks[finger_tip].y < landmarks[finger_pip].y - 0.02

    def is_thumb_up(self, landmarks):
        # Detectar si el pulgar está extendido
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # El pulgar está extendido si la punta está más lejos del centro de la mano
        # que las articulaciones anteriores
        wrist = landmarks[0]
        
        # Distancia de la punta del pulgar a la muñeca
        tip_distance = self.get_distance(thumb_tip, wrist)
        # Distancia de la articulación del pulgar a la muñeca
        joint_distance = self.get_distance(thumb_ip, wrist)
        
        return tip_distance > joint_distance + 0.02
    
    def is_L_gesture(self, landmarks):
        # Gesto L: índice y pulgar extendidos, otros dedos cerrados
        index_up = self.is_finger_up(landmarks, 8, 6)
        thumb_up = self.is_thumb_up(landmarks)
        middle_down = not self.is_finger_up(landmarks, 12, 10)
        ring_down = not self.is_finger_up(landmarks, 16, 14)
        pinky_down = not self.is_finger_up(landmarks, 20, 18)
        return index_up and thumb_up and middle_down and ring_down and pinky_down
    
    def is_pointing_gesture(self, landmarks):
        # Solo índice arriba, pulgar cerrado
        index_up = self.is_finger_up(landmarks, 8, 6)
        thumb_down = not self.is_thumb_up(landmarks)
        middle_down = not self.is_finger_up(landmarks, 12, 10)
        ring_down = not self.is_finger_up(landmarks, 16, 14)
        pinky_down = not self.is_finger_up(landmarks, 20, 18)
        return index_up and thumb_down and middle_down and ring_down and pinky_down

    def is_two_fingers_gesture(self, landmarks):
        # Índice y medio arriba
        index_up = self.is_finger_up(landmarks, 8, 6)
        middle_up = self.is_finger_up(landmarks, 12, 10)
        ring_down = not self.is_finger_up(landmarks, 16, 14)
        pinky_down = not self.is_finger_up(landmarks, 20, 18)
        return index_up and middle_up and ring_down and pinky_down



    def smooth_coordinates(self, new_x, new_y):
        # Agregar al buffer de posiciones
        self.position_buffer.append((new_x, new_y))
        if len(self.position_buffer) > self.position_buffer_size:
            self.position_buffer.pop(0)
        
        # Promedio de posiciones en el buffer
        if len(self.position_buffer) >= 3:
            avg_x = sum(pos[0] for pos in self.position_buffer) / len(self.position_buffer)
            avg_y = sum(pos[1] for pos in self.position_buffer) / len(self.position_buffer)
        else:
            avg_x, avg_y = new_x, new_y
        
        # Suavizado exponencial
        smooth_x = int(self.prev_mouse_x * self.smooth_factor + avg_x * (1 - self.smooth_factor))
        smooth_y = int(self.prev_mouse_y * self.smooth_factor + avg_y * (1 - self.smooth_factor))
        
        # Filtro de movimiento mínimo
        dx = abs(smooth_x - self.prev_mouse_x)
        dy = abs(smooth_y - self.prev_mouse_y)
        
        if dx < self.min_movement and dy < self.min_movement:
            return int(self.prev_mouse_x), int(self.prev_mouse_y)
        
        self.prev_mouse_x, self.prev_mouse_y = smooth_x, smooth_y
        return smooth_x, smooth_y
    
    def get_stable_gesture(self, current_gesture):
        self.gesture_buffer.append(current_gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        
        if len(self.gesture_buffer) < self.buffer_size:
            return None
        
        # Retornar el gesto más común en el buffer
        gesture_counts = {}
        for gesture in self.gesture_buffer:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        return max(gesture_counts, key=gesture_counts.get)

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if self.show_camera:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                landmarks = hand_landmarks.landmark
                index_tip = landmarks[8]  # Punta del dedo índice
                h, w, _ = frame.shape
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                
                # Mapear coordenadas a pantalla usando área reducida de cámara
                screen_w, screen_h = pyautogui.size()
                
                # Usar solo el 60% central de la cámara para mapear a toda la pantalla
                margin = 0.2  # 20% de margen en cada lado
                normalized_x = (index_tip.x - margin) / (1 - 2 * margin)
                normalized_y = (index_tip.y - margin) / (1 - 2 * margin)
                
                # Limitar valores entre 0 y 1
                normalized_x = max(0, min(1, normalized_x))
                normalized_y = max(0, min(1, normalized_y))
                
                screen_x = int((1 - normalized_x) * screen_w)
                screen_y = int(normalized_y * screen_h)
                
                # Detectar gestos
                is_L = self.is_L_gesture(landmarks)
                is_pointing = self.is_pointing_gesture(landmarks)
                is_two_fingers = self.is_two_fingers_gesture(landmarks)
                
                # Determinar gesto actual
                current_gesture = None
                if is_L:
                    current_gesture = 'move'
                elif is_pointing:
                    current_gesture = 'click'
                elif is_two_fingers:
                    current_gesture = 'scroll'
                else:
                    current_gesture = 'none'
                
                # Obtener gesto estable
                stable_gesture = self.get_stable_gesture(current_gesture)
                
                if stable_gesture == 'move':
                    # Mover mouse con suavizado
                    smooth_x, smooth_y = self.smooth_coordinates(screen_x, screen_y)
                    pyautogui.moveTo(smooth_x, smooth_y)
                    self.last_mouse_x, self.last_mouse_y = smooth_x, smooth_y
                    self.prev_y = 0
                    
                    if self.show_camera:
                        cv2.circle(frame, (x, y), 8, (0, 255, 0), 2)
                        cv2.putText(frame, "MOVE", (x-25, y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                elif stable_gesture == 'click':
                    # Click manteniendo posición del mouse
                    current_time = time.time()
                    if current_time - self.last_click_time > self.click_cooldown:
                        if self.last_mouse_x != 0 and self.last_mouse_y != 0:
                            pyautogui.click(self.last_mouse_x, self.last_mouse_y)
                        else:
                            pyautogui.click()
                        self.last_click_time = current_time
                    
                    if self.show_camera:
                        cv2.circle(frame, (x, y), 12, (0, 0, 255), -1)
                        cv2.putText(frame, "CLICK", (x-30, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                elif stable_gesture == 'scroll':
                    # Scroll más lento con cooldown
                    current_time = time.time()
                    if self.prev_y != 0 and current_time - self.last_scroll_time > self.scroll_cooldown:
                        dy = screen_y - self.prev_y
                        if abs(dy) > 5:  # Umbral más alto
                            # Scroll más lento
                            if dy > 0:
                                pyautogui.scroll(-1)  # Scroll hacia abajo (más lento)
                            else:
                                pyautogui.scroll(1)   # Scroll hacia arriba (más lento)
                            self.last_scroll_time = current_time
                    
                    self.prev_y = screen_y
                    
                    if self.show_camera:
                        cv2.circle(frame, (x, y), 10, (255, 0, 255), 2)
                        cv2.putText(frame, "SCROLL", (x-35, y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                
                else:
                    # Reset
                    self.prev_y = 0
        else:
            # Reset buffer cuando no hay manos
            self.gesture_buffer = []
        
        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("Detector de gestos iniciado...")
        print("Gesto L (índice+pulgar): Mover mouse")
        print("Solo índice (pulgar cerrado): Click")
        print("Dos dedos (índice+medio): Scroll vertical")
        if self.show_camera:
            print("Presiona 'q' para salir")
        else:
            print("Ejecutándose en segundo plano. Presiona Ctrl+C para salir")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = self.process_frame(frame)
                
                if self.show_camera:
                    cv2.imshow('Control por Gestos', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    cv2.waitKey(1)
                    
        except KeyboardInterrupt:
            print("\nDeteniendo detector de gestos...")
        finally:
            cap.release()
            if self.show_camera:
                cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Control de PC por gestos')
    parser.add_argument('--camera', action='store_true', help='Mostrar ventana de cámara')
    args = parser.parse_args()
    
    controller = GestureController(show_camera=args.camera)
    controller.run()

if __name__ == "__main__":
    main()
