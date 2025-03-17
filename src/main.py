import lib.configuration as configuration
import ujson  # type: ignore
from lib.http_client import HTTPClient  # Importa correctamente la clase HTTPClient
import time  # Importar para el bucle infinito

# Variables globales
lora = None
url = None
http = None

def initial_configuration():
    global lora, url, http  # Asegurar que las variables globales se actualicen correctamente

    print("Opening configuration file")
    try:
        configuration.led_on(2)

        # Intentar abrir el archivo de configuración
        with open("config.json", "r") as f:
            config = ujson.load(f)

        print("Configuration file opened successfully\nConnecting to network")
        configuration.led_on(3)

        # Conectar a Wi-Fi
        configuration.connect_wifi(config["wifi"]["ssid"], config["wifi"]["password"])

        # Guardar la URL de la API
        url = config["api"]["url"]

    except OSError:
        print("Not able to open configuration file")
        configuration.led_on(10)
        configuration.led_off(2)
        configuration.led_off(3)
        return  # Salimos de la función si no se pudo abrir el archivo

    # Inicializar LoRa
    lora = configuration.init_lora()
    if lora is None:
        print("Error: LoRa module not initialized")
        return
    configuration.led_on(4)

    # Inicializar HTTP Client con o sin certificado TLS
    cert_path = config["api"].get("cert_path")  # Verifica si hay un certificado en la configuración
    http = HTTPClient(cert_path=cert_path)  # Crear instancia de HTTPClient
    configuration.led_on(5)

    # Obtener hora del servidor NTP
    configuration.set_time()
    configuration.led_on(6)


def lora_receive_handler(data):
    """ Función para manejar los mensajes recibidos por LoRa """
    configuration.led_on(9)
    data = data.decode("utf-8")

    current_time = time.localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])

    if data[-1] : 
        status = 'ok'
    else:
        status = 'Error'

    print(f"[{formatted_time}]: Device: {data[:6]} status: {status} ")

    # Enviar datos a la API solo si `http` y `url` están definidos
    #if http and url:
    #    response = http.post(url, data)
    #    print(f"HTTP Response: {response}")

    configuration.led_off(9)


def main():
    # Configuración inicial
    configuration.init_leds()
    configuration.led_on(1)
    print("Starting bridge ...")
    initial_configuration()
    print("Bridge started successfully")

    # Verificar que LoRa fue inicializado correctamente
    if lora is None:
        print("LoRa initialization failed, exiting...")
        return

    # Configurar LoRa para recibir datos en modo RX continuo
    lora.on_recv(lora_receive_handler)
    lora.recv()  # Activa modo RX_CONTINUOUS

    print("ESP32 en espera de mensajes LoRa...")

    # Mantener el programa en ejecución
    while True:
        time.sleep(1)  # Evitar que el bucle consuma toda la CPU


if __name__ == "__main__":
    main()