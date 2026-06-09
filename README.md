# Syncky #

## Introducción
Syncky es un proyecto de Geckoscript que se desarrolló para Farivi en el cual se sincronizan los sistemas locales instalados en las sucursales de forma automática.

Actualmente Farivi cuenta con 9 sucursales:

* Huajuapan
* Casimiro
* 5 de Febrero
* Tlaxiaco
* Tlaxiaco Menudeo
* Putla
* Juxtlahuaca
* Juxtlahuaca Centro 
* Mina

Las 9 sucursales se encuentran interconectadas a través de Tailscale creando una red privada virtual. También se encuentra dentro de esta red el servidor productivo gsiwsvprd04 que es una máquina virtual dentro de gsiwsvprd03 (servidor de respaldos) y es en este servidor donde se encuentra corriendo Syncky.

## Releases
### Release v3.3 (10 de diciembre de 2024)
Se se agrega la ejecucuon de una query para renombrar la tabla go_productos_precios a go_productos_precios_temp para el sistema local.
* src/conf.py
* src/main.py

### Release v3.2 (31 de julio de 2024)
Se actualiza los archivos de configuración:
* src/conf.py
* src/main.py
* .env

Para actualizar los sistemas locales en la versión Claudia
### Release v3.1 (3 de abril de 2024)
* Se agrega la sucursal Mina

### Release v3.0 (3 de agosto de 2023)
* Se agrega el script remote_admin.py, el cual permite:
  * Ejecutar comandos en equipos de forma remota utilizando WinRM 
  * Prender y apagar equipos de forma remota.
* Se agregan 4 crones que encienden y apagan las cajas de emergencia de las sucursales dos veces al día para que se sincronizen los sistemas locales.
* Se agregan las 4 cajas de emergencias al proceso de sincronización de los sistemas locales.

### Release v2.1 (28 de julio de 2023)
* Se agregan los equipos de respaldo (emergencia) de las sucursales

### Release v2 (23 de julio de 2023)
* Se actualiza el script para que funcione con la nueva versión del sistema local
* Se parametrizan variables de entorno
* Se actualiza la versión de Filebeat a la versión 8.8.2

### Release v1 (27 de enero de 2023)
* Primer versión estable de sincronización de los sistemas locales 

## Requerimientos

Para poder sincronizar los sistemas locales es necesario tener instalado y configurado en cada equipo:

* FileZilla Server
* WinRM
* 7zip
* Wamp
* Sistema administrala Claudia

Los pasos a seguir para la instalación y configuración de cada uno de los puntos anteriores se detallan en los procedimientos SST-001 y SST-003.

## Funcionamiento

Esta solución utiliza 2 contenedores (Docker):

* core - Aqui reside el script de python
* filebeat - Este contenedor se utiliza para enviar los logs al servidor de elastic

La sincronización de los sistemas locales se realiza en 6 pasos y el script utiliza multihilos a partir del punto 3:

1. Se conecta al servidor gsiwsvprd01 a través de SSH y realiza el respaldo de 5 tablas (go_clientes, go_productos, go_productos_precios_temp, go_usuarios y go_usuarios_sucursal) de la base de datos de Farivi y lo comprime en tgz.
2. A través de SCP descarga el respaldo del servidor al contenedor.
3. Sube el respaldo comprimido a cada uno de los sistemas locales a través de FTP (FileZilla Server).
4. Descomprime los respaldos utilizando 7zip a travpes de WinRM
5. Importa el respaldo a MySQL a través de WinRM
6. Ejecuta dos Queries utilizando WinRM para actualizar las existencias de los productos

Los logs que genera este script son enviados a Elastic, en Elastic se crearon 2 visualizaciones:

* Discover - 91. GS > Filebeat > Syncky
* Dashboard - 91. GS > Farivi > Syncky

Elastic envía automáticamente las alertas al canal de Slack de GeckoScript.

Syncky se ejecuta automáticamente todos los días a las 10:00 AM a partir de un CRON.

## Configuraciones

Existen dos archivos de configuración donde se establecen los valores necesarios para realizar las conexiones:

* conf.py - Credenciales de acceso del servidor Sugarbaby (iWeb), y FTP y WinRM de sucursales
* filebeat.yml - Credenciales de elastic para el envío de los logs

## Automatización

Se crearon 4 script en Bash:

* _start.sh - Inicia Syncky
* _stop.sh - Detiene Syncky
* _restart.sh - Reinicia Syncky
* _remove.sh - Elimina por completo Synky (destruye contenedores, volúmenes y redes)

## Extras

Query para eliminar los registros de Elastic


```json
POST /.ds-filebeat-*/_delete_by_query
{
  "query": {
    "match": {
      "log.file.path": "/syncky/logs/syncky.log"
    }
  }
}
```