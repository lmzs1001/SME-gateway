""""Configuración del modulo LoRa"""
# SPI pins
SCK  = 18
MOSI = 23
MISO = 19
# Chip select
CS   = 5 #NSS
# Receive IRQ
RX   = 2 #DIO01
RST = 17


leds = (12, 14, 27, 26, 25, 33, 32, 15, 4, 16)

from machine import Pin # type: ignore
from utime import sleep # type: ignore
"""Configuración d leds """
def led_on (led): 
    Pin(leds[led-1], Pin.OUT).on() 
        
def led_off (led): 
    Pin(leds[led-1], Pin.OUT).off()

def init_leds ():
    for i in leds : 
        Pin(i, Pin.OUT).on()
        sleep (1)
        Pin(i, Pin.OUT).off()

from lora import LoRa
from machine import Pin, SPI # type: ignore
"""Configuración de Wimodulo lora"""
def init_lora (): 
    spi = SPI(
        1,
        baudrate=10000000,
        sck=Pin(SCK, Pin.OUT, Pin.PULL_DOWN),
        mosi=Pin(MOSI, Pin.OUT, Pin.PULL_UP),
        miso=Pin(MISO, Pin.IN, Pin.PULL_UP),
    )
    spi.init()

    lora = LoRa(
        spi,
        cs=Pin(CS, Pin.OUT),
        rx=Pin(RX, Pin.IN),
        reset = Pin (RST, Pin.OUT),
        frequency=915.0,
        bandwidth=125000,
        spreading_factor=7,
        coding_rate=5,
    )

    return lora




"""Configuración de Wifi"""
import network # type: ignore

def connect_wifi(ssid, password):
    """Conectar el ESP32 a WiFi"""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    
    while not sta.isconnected():
        pass  # Esperar conexión
    
    print("Connected to network:", sta.ifconfig())



import socket

NTP_SERVER = "pool.ntp.org"  # Servidor NTP público
NTP_PORT = 123
NTP_DELTA = 2208988800 

import socket
import struct
import time
import machine # type: ignore

def get_ntp_time():
    """Obtiene la hora del servidor NTP y la convierte a formato Unix"""
    addr = socket.getaddrinfo(NTP_SERVER, NTP_PORT)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)  # Tiempo de espera para respuesta NTP
    
    ntp_query = b'\x1b' + 47 * b'\0'  # Paquete de consulta NTP
    s.sendto(ntp_query, addr)
    
    try:
        msg, _ = s.recvfrom(48)  # Recibir respuesta NTP (48 bytes)
    except:
        print("Error al obtener la hora NTP")
        s.close()
        return None
    
    s.close()
    
    t = struct.unpack("!12I", msg)[10] - NTP_DELTA  # Extraer timestamp
    return time.localtime(t)

def set_time():
    """Establece la hora del ESP32 usando la respuesta NTP"""
    GMT_OFFSET = -6 * 3600  # Para UTC-6 (ejemplo: México, Centroamérica)
    t = get_ntp_time()
    if t:
        machine.RTC().datetime((t[0], t[1], t[2], 0, t[3], t[4], t[5], 0))
        print("Hora actualizada:", time.localtime())
    else:
        print("No se pudo actualizar la hora.")
