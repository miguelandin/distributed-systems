from meteo_stub import MeteoStub

m = MeteoStub('127.0.0.1', 5002)
print(m.temperatura('Madrid'))
print(m.humedad('Madrid'))
print(m.pronostico('Madrid'))
print(m.futuro('Madrid'))
