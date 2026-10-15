def info_imagen(nombre):
    return {'archivo':nombre,'width':1920,'height':1080,'format':'JPEG'}
def escala_grises(nombre):
    return f'{nombre} procesada en escala de grises'
def redimensionar(nombre,width,height):
    return {'archivo':nombre,'width':width,'height':height}
