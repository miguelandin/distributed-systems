Se ha creado la estructura inicial del proyecto:
1. `deployment/`: Directorio en el que estará el Dockerfile.
2. `docs/`: Aquí irá la documentación final de la práctica junto al `CHANGELOG.md` que se usará para apoyar el proceso de la documentación final.
3. `k8s`: Estarán los `.yaml` que usará kuberenetes para desplegarse.
4. `docs/`: Contendrá evidencias (imágenes, gifs, videos) para la documentación.

En cuanto al código python de la imagen del docker, se usará el directorio por encima del proyecto, `rpc_assignment` para no repetir código y por si en algún futuro sehace un cambio en la práctica 1, los cambias se aplicarán también en la práctica 2.

---

Ahora he creado el Dockerfile, el cual, como mencioné antes, usa el código del `rpc_assignment`, por lo que el comando de `docker build ...` debe de ejecutarse desde `assignment/` para que funcione. También he creado un script de bash que crea la imagen del docker desde cualquier directorio (recomiendo usar esto).

También se ha subido en `assets/` una imagen que demuestra que el contenedor de docker funciona correctamente.
Finalmente, en la documentación he añadido un fichero con los prompts de IA usados durante la práctica.
