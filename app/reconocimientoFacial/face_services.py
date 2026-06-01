import face_recognition
import numpy as np
import json
import os
import cv2
from django.conf import settings
from app.estudiante.models import Estudiante
from django.http import StreamingHttpResponse

import mediapipe as mp
from django.conf import settings


#configuracion de mediapipe para dibujar la malla facial
mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
FacemeshObject = mpFaceMesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
ConfigDraw = mpDraw.DrawingSpec(thickness=1, circle_radius=1, color=(255,255,255))
ultimo_reconocimiento = {}

#generamos el encoding a partir de la imagen del estudiante (DireccionCarre)
def generar_encoding(ruta_relativa):
    ruta = os.path.join(settings.MEDIA_ROOT, ruta_relativa)

    if not os.path.exists(ruta):
        return None

    try:
        # Usar PIL para cargar y convertir a RGB de forma consistente
        img = Image.open(ruta).convert('RGB')
        img_array = np.array(img)  # ahora es uint8, shape (H,W,3) en RGB
    except Exception as e:
        return None

    # face_recognition requiere array contiguo
    img_array = np.ascontiguousarray(img_array, dtype=np.uint8)

    face_locations = face_recognition.face_locations(img_array)
    if not face_locations:
        return None

    encodings = face_recognition.face_encodings(img_array, face_locations)
    if not encodings:
        return None

    return json.dumps(encodings[0].tolist())


#determinamos si el encodign registrado es valido o no
def obtener_estudiantes_con_encoding():
    estudiantes = Estudiante.objects.exclude(encoding__isnull=True)

    data = []
    for est in estudiantes:
        encoding = np.array(json.loads(est.encoding))
        data.append((est, encoding))

    return data


def reconocer_estudiante(frame):
    if frame is None:
        return None

    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)

    #Convertir a RGB
    if len(frame.shape) == 3:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    elif len(frame.shape) == 2:
        rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    else:
        return None

    rgb = np.ascontiguousarray(rgb)

    ubicaciones = face_recognition.face_locations(rgb)

    if not ubicaciones:
        return None

    encodings = face_recognition.face_encodings(rgb, ubicaciones)

    estudiantes_db = obtener_estudiantes_con_encoding()

    for encoding in encodings:
        for estudiante, encoding_db in estudiantes_db:
            distance = face_recognition.face_distance([encoding_db], encoding)[0]

            if distance < 0.5:
                return estudiante
                

    return None


#reconocimiento bounding box y nombre
def procesar_frame(frame):
    estudiante_encontrado = None

    if frame is None:
        return frame, None
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = np.ascontiguousarray(rgb)

    ubicaciones = face_recognition.face_locations(rgb)

    if ubicaciones:
        encodings = face_recognition.face_encodings(rgb, ubicaciones)
        estudiantes_db = obtener_estudiantes_con_encoding()

        for (top, right, bottom, left), encoding in zip(ubicaciones, encodings):
            nombre = "Estudiante Desconocido"

            for estudiante, encoding_db in estudiantes_db:
                distance = face_recognition.face_distance([encoding_db], encoding)[0]
                if distance < 0.5:
                    nombre = f"{estudiante.nombre} {estudiante.apellido}"
                    estudiante_encontrado = estudiante
                    break
                

            #dibujar bounding box color blanco
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), 2)

            #nombre con color
            cv2.putText(frame, nombre, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0, 255, 0) 
                        if estudiante_encontrado 
                        else (0, 0, 255), 2)

    # malla facial con mediapipe
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = FacemeshObject.process(frameRGB)

    if res.multi_face_landmarks:
        for rostros in res.multi_face_landmarks:
            # Dibujar la malla facial
            mpDraw.draw_landmarks(frame, rostros, mpFaceMesh.FACEMESH_CONTOURS, ConfigDraw, ConfigDraw)
    return frame, estudiante_encontrado

def gen_frames():
    cap = cv2.VideoCapture(0) 

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame, estudiante = procesar_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')