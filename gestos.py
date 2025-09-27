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
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.show_camera = show_camera
        
        # Variables para control de gestos
        self.prev_x, self.prev_y = 0, 0
        self.click_threshold = 30
        self.scroll_sensitivity = 3
        self.last_click_time = 0
        self.click_cooldown = 0.3
        
        # Configurar pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01

    def get_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def is_pinch_gesture(self, landmarks):
        # Distancia entre pulgar e índice
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = self.get_distance(thumb_tip, index_tip)
        return distance < 0.05

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if self.show_camera:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                landmarks = hand_landmarks.landmark
                
                if self.is_pinch_gesture(landmarks):
                    # Obtener posición del índice para control del cursor
                    index_tip = landmarks[8]
                    h, w, _ = frame.shape
                    x = int(index_tip.x * w)
                    y = int(index_tip.y * h)
                    
                    # Mapear coordenadas de la cámara a la pantalla
                    screen_w, screen_h = pyautogui.size()
                    screen_x = int((1 - index_tip.x) * screen_w)  # Invertir X para efecto espejo
                    screen_y = int(index_tip.y * screen_h)
                    
                    current_time = time.time()
                    
                    if self.prev_x == 0 and self.prev_y == 0:
                        # Primera detección de pinch - hacer click
                        if current_time - self.last_click_time > self.click_cooldown:
                            pyautogui.click(screen_x, screen_y)
                            self.last_click_time = current_time
                        self.prev_x, self.prev_y = screen_x, screen_y
                    else:
                        # Movimiento con pinch - hacer scroll
                        dx = screen_x - self.prev_x
                        dy = screen_y - self.prev_y
                        
                        if abs(dy) > 5:  # Threshold mínimo para scroll
                            scroll_amount = int(dy / self.scroll_sensitivity)
                            pyautogui.scroll(-scroll_amount)
                        
                        self.prev_x, self.prev_y = screen_x, screen_y
                    
                    if self.show_camera:
                        cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                        cv2.putText(frame, "PINCH", (x-30, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    # Reset cuando no hay pinch
                    self.prev_x, self.prev_y = 0, 0
        
        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Detector de gestos iniciado...")
        print("Haz pinch con pulgar e índice para hacer click")
        print("Mantén el pinch y mueve la mano para hacer scroll")
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
                    cv2.waitKey(1)  # Necesario para el procesamiento
                    
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