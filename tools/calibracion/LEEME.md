# Calibración del diccionario ROS

`forms2apex` lee los `.fmt`/`.mmt` de Forms 6i, donde las propiedades están identificadas solo por
**número**. `config/diccionario_ros.yaml` traduce cada número a la propiedad oficial de Forms, con su
tipo y su valor por defecto. Ese diccionario se genera con esta calibración. Se corre una vez, o cada
vez que aparecen forms que usan propiedades nuevas, y **solo en una máquina con Forms 6i instalado**.
La herramienta final no necesita Forms ni la Open API.

## Pasos

1. Por cada módulo de calibración, tener el par binario + texto en `samples/` (por ejemplo
   `X.fmb` y `X.fmt`, convertido con `ifcmp60 module=X.fmb script=YES batch=YES logon=NO`).
2. Volcar el binario con la Open API. Es **solo lectura**: no guarda ni modifica el `.FMB`/`.MMB`.
   Debe correr en PowerShell de 32 bits:

   ```powershell
   C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass `
     -File tools\calibracion\volcar_api.ps1 -Modulo samples\X.fmb -Salida tools\calibracion\volcados\X.api.tsv
   ```

3. Calibrar con todos los pares disponibles:

   ```powershell
   .venv\Scripts\python.exe tools\calibracion\calibrar.py `
     samples\STKC007.fmt tools\calibracion\volcados\STKC007.api.tsv `
     samples\fini018.fmt tools\calibracion\volcados\fini018.api.tsv `
     samples\WAPIDEMO.mmt tools\calibracion\volcados\WAPIDEMO.api.tsv
   ```

4. Revisar `reporte_calibracion.md`. Lo que la estadística no pueda resolver se corrige en
   `ajustes_manuales.yaml`, siempre con su evidencia. Esos ajustes se reaplican en cada calibración.

## Cómo decide

Para cada (número ROS, tipo de objeto) elige la propiedad de la API que cumple tres cosas:
- coincide en valor;
- la API marca como **no default** donde el `.fmt` la graba;
- la API marca como **default** donde el `.fmt` no la graba.

El `.fmt` solo graba valores distintos del default, así que la propiedad correcta cumple las tres.
El detalle está en el docstring de `calibrar.py`.
