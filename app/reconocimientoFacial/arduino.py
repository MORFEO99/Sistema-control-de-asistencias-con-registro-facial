import serial
import time

PUERTO_ARDUINO = 'COM3'
BAUDRATE = 9600

arduino = None


def conectar_arduino():

    global arduino

    # evitar reconexion multiple
    if arduino is None:

        try:

            arduino = serial.Serial(
                PUERTO_ARDUINO,
                BAUDRATE,
                timeout=1
            )

            # esperar inicializacion Arduino
            time.sleep(2)

            print("Arduino conectado")

        except Exception as e:

            print("Error conectando Arduino:", e)

            arduino = None


def abrir_puerta():

    global arduino

    conectar_arduino()

    if arduino is None:
        return

    try:

        # enviar comando al Arduino
        arduino.write(b'1')

        print("Puerta abierta")

    except Exception as e:

        print("Error enviando datos:", e)

        arduino = None