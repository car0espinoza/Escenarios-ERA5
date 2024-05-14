import cdsapi
import netCDF4 as nc
import math
import pandas as pd
import random
from datetime import datetime
from datetime import timedelta


print("Este programa entrega multiples escenario meteorologicos para se utilizado en Cell2Fire")
print("La ubicación debe ser entregada en coordenadas geográficas")

#Modelo de combustible
print("Qué tipo de de modelo de combustible usara: ")
sc = int(input("Ingrese 1 para kitral o 2 para Scott&Burgan: "))
if sc == 1:
    print("Ha elegido la opción Kitral")
elif sc == 2:
    print("Ha elegido la opción Scott&Burgan")
    FS = int(input("Ingrese el tipo de fireScenario (Live & Dead Fuel Moisture Content Scenario [1=dry..4=moist]): "))
    if FS >= 1 and FS <= 4:
        print("FireScenario= " + str(FS))
    else:
        exit("Opción no valida")
else:
    exit("Opción no valida")

#lat, lon
lat=float(input("ingrese la latitud en coordenadas geograficas (ejem: -33.0): "))
lon=float(input("Ingrese la longitud en coordenas geograficas (ejem: -71.0): "))

#numero de horas
n=int(input("Cuantos escenario desea: "))
H=int(input("Cuantas horas debe durar el scenario: "))

"""
n=10
sc=2
FS=1

lat=33.2
lon=-71.0
H=10
"""

##########################
#######FUNCIONES##########
##########################

#funcion que calcula el angulo de cell2fire a partir de las componentes
def angulo_c2f(u,v):
    if v<0:
        theta=round(math.degrees( math.atan(u/v))+180,1)
    elif v==0 and u<0:
        theta= 270
    elif v>0 and u<0:
        theta= round(math.degrees(math.atan(u/v))+360,1)
    elif v>0 and u>=0:
        theta= round(math.degrees(math.atan(u/v)),1)
    elif v==0 and u>0:
        theta= 90
    else:
        theta=math.nan
    return theta

def magnitud(u,v):
    m= math.sqrt(u*u+v*v)
    return m

def mps_kmph(mps):
    kmph=mps*3.6
    kmph=round(kmph,1)
    return kmph

def humedad_relativa(t,td):
    hr=(math.exp((17.625*td)/(243.04+td)))/(math.exp((17.625*t)/(243.04+t)))*100
    return round(min(hr,100),0)
################################################################################



c = cdsapi.Client()
if lat<0:
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature',
            ],
            'year': '2023',
            'month': [
                '01',
            ],
            'day': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00',
            ],
            'area': [
                lat, lon, lat,lon,
            ],
        },
        'download.nc')

elif lat>=0:
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature',
            ],
            'year': '2023',
            'month': ['07',
            ],
            'day': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00',
            ],
            'area': [
                lat, lon, lat,lon,
            ],
        },
        'download.nc')


else:
    print("Opción no valida")



ds = nc.Dataset('download.nc')
comp_v = ds["v10"][:, :, :]
comp_u = ds["u10"][:, :, :]
temp = ds["t2m"][:, :, :] - 273.15
dew = ds["d2m"][:, :, :] - 273.15


angulo=[]
velocidad=[]
temperatura=[]
HR=[]

for i in range(len(comp_v)):
    # angulo
    alfa = angulo_c2f(comp_u[i], comp_v[i])
    angulo.append(alfa)
    # magnitud
    mag = magnitud(comp_u[i], comp_v[i])
    velocidad.append(mps_kmph(mag))
    # temperatura
    temperatura.append(round(float(temp[i]), 1))
    # humedad
    hr = humedad_relativa(temp[i], dew[i])
    HR.append(round(hr, 1))

dato = pd.DataFrame()
dato["WS"] = velocidad
dato["WD"] = angulo
dato["TMP"] = temperatura
dato["RH"] = HR


r=random.randint(0,len(velocidad)-H-1)

#Fechas
hoy=datetime.now()
fecha_i=datetime(int(hoy.year),int(hoy.month),int(hoy.day),int(hoy.hour),0,0)
fechas=[]
for i in range(H):
    fechas.append(fecha_i+timedelta(hours=i))


for j in range(n):
    r = random.randint(0, len(velocidad) - H - 1)
    if sc == 1:
        df = pd.DataFrame()
        df["Scenario"] = ["ERA5"] * H
        df["datetime"] = fechas
        df["WS"] = dato["WS"].iloc[r:r + H].tolist()
        df["WD"] = dato["WD"].iloc[r:r + H].tolist()
        df["TMP"] = dato["TMP"].iloc[r:r + H].tolist()
        df["RH"] = dato["RH"].iloc[r:r + H].tolist()
        df.to_csv("weather"+str(j+1)+".csv", index=False)

    elif sc == 2:
        df = pd.DataFrame()
        df["Scenario"] = ["ERA5"] * H
        df["datetime"] = fechas
        df["WS"] = dato["WS"].iloc[r:r + H].tolist()
        df["WD"] = dato["WD"].iloc[r:r + H].tolist()
        df["FireScenario"] = [FS] * H
        df.to_csv( "weather" + str(j + 1) + ".csv", index=False)

print("Sus archivos se han descargado correctamente")