Archivos para conectar a Blynk.io

Los archivos en esta sección son modificaciones de los disponibles en

https://github.com/Blynk-Technologies/Blynk-MQTT-Samples/tree/main/MicroPython

funciona en micropython v1.27

Install_blynk.py es un script que permite enlazarse a internet y descarga en el ESP32 los siguientes archivos:

Boot.py   libera memoria ocupada por modulos dejandos en memoria

Config.py contiene las claves de conexión a Wi-Fi y a Blynk.io, debe personalizarse para cada usuario

Demo.py   programa de demostración de enlace, control del LED de la terminal P2 y simulación de lectura de sensor de temperatura.


ISRG_Root_X1.der contine credenciales para el enlace seguro a Blynk.io usando SSL

En la carpeta /lib se encuentra el módulo modificado para el enlace via MQTT del ESP32 a Blynk.io
