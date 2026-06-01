import base64
import numpy as np
import cv2
from django.shortcuts import render
from app.reconocimientoFacial.face_services import procesar_frame
from app.asistencia.services import registrar_asistencia
from django.utils import timezone
from app.reconocimientoFacial.arduino import abrir_puerta

def tomar_asistencia(request):
    if request.method == "POST":
        data_url = request.POST.get("imagen")

        if not data_url:
            return render(request, "asistencia/resultado.html", {
                "mensaje": "No se recibió imagen"
            })

        #convertir base64 a imagen OpenCV
        try:
            format, imgstr = data_url.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception as e:
            return render(request, "asistencia/resultado.html", {
                "mensaje": f"Error al decodificar imagen: {e}"
            })

        #procesamos el frame con reconocimiento facial
        frame_procesado, estudiante = procesar_frame(frame)

        #convertir imagen procesada a base64 para mostrar en resultado
        _, buffer = cv2.imencode('.jpg', frame_procesado)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        ahora = timezone.localtime(timezone.now())
        hora_registro = ahora.strftime("%H:%M")
        fecha_registro = ahora.strftime("%d/%m/%Y")

        #si no es reconocido, estudiante no se lo registrara
        if not estudiante:
            return render(request, "asistencia/resultado.html", {
                "mensaje": "Estudiante no encontrado",
                "imagen": img_base64,
                "hora_registro": hora_registro,
                "fecha_registro": fecha_registro
            })

        #registramos la asistencia si el estudiante fue reconocido
        asistencia, mensaje = registrar_asistencia(estudiante)
        if asistencia:
            abrir_puerta()
        
        return render(request, "asistencia/resultado.html", {
            "mensaje": mensaje,
            "estudiante": estudiante,
            "asistencia": asistencia,
            "imagen": img_base64,
            "hora_registro": hora_registro,
            "fecha_registro": fecha_registro
        })

    #redirigimos a la página de tomar asistencia para mostrar la cámara
    return render(request, "asistencia/tomar_asistencia.html")
