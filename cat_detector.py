import serial
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import cv2
import time


try:
    arduino = serial.Serial('/dev/pts/1', 9600, timeout=1)
except serial.SerialException:
    arduino = None
    print("Arduino não conectado. Modo simulado ativado.")


model = MobileNetV2(weights="imagenet")


def detect_cat(frame):
    img_array = cv2.resize(frame, (224, 224))
    img_array = img_to_array(img_array)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
    for pred in decoded_predictions:
        if "cat" in pred[1].lower():
            return True
    return False


cap = cv2.VideoCapture("https://192.168.0.14:8080/video")

last_dispense_time = 0
dispense_count = 0
last_detection_time = 0


def dispense_food():
    global last_dispense_time, dispense_count
    current_time = time.time()

    if current_time - last_dispense_time >= 14400:
        dispense_count = 0

    if dispense_count < 2:
        last_dispense_time = current_time
        dispense_count += 1

        if arduino:
            arduino.write(b'  DETECTADO  ')
        else:
            print("Simulação: Portinha aberta!")

        return "Ração liberada!"
    else:
        return "Limite atingido. Aguarde 4 horas."


while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    if current_time - last_detection_time >= 10:
        if detect_cat(frame):
            message = dispense_food()
            cv2.putText(frame, f"Gato detectado! {message}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Nenhum gato detectado.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        last_detection_time = current_time

    resized_frame = cv2.resize(frame, (640, 480))
    cv2.imshow("Detector de Gatos", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
