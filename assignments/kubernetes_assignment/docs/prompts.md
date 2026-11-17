Vale. Como ves tengo que completar la práctica 2. El enunciado es el png adjunto. Los otros dos archivos (pdf, txt) son ejercicios de ejemplo de como montar y desplegar docker y kubernetes. El Documentation.md es la documentación del código de la práctica anterior para que sepas sobre que estamos montando el docker.También tienes adjunto el repositorio de la asignatura.
a la hora de montar el docker, solo habría que montarlo del servidor no? por que habría que meter en la misma imagen al cliente?
en la estructura del directorio para la practica dos, que forma debería de tener? Tenía pensado poner un docs/ un README.md. Pero por ejemplo el DockerFile y .yaml no sé donde iría. ¿Cual es el estandar de la industria a la hora de situar estos archivos?
no sería mejor, para no repetir código que coja el common/ y server/ de la práctica 1? además, así si hago un cambio en el assignment 1 por lo que sea, se actualizaría en el assignment 2.
Explícame que hace cada línea del Dockerfile.
por qué has elegido el puerto 5000 para exponer? lo dice el enunciado? es un estándar?
 He hecho un script dentro de deployment para que sea más cómodo de ejecutar el docker build. Seguro que hay una forma de coger el directorio assignments mejor.
 [docker images]Qué significa esta salida? No debería de tener solo la imagén de rpc-server:1.0? por qué tengo python:3.13-slim también? 
Tengo la imagen corriendo pero parece que el cliente ha fallado. Este error es porque el cliente está mal o es el servidor el problema?
