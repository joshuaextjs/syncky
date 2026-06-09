#!/usr/bin/env python
# -*- coding: utf-8 -*-

syncky_conf = {
    "temp_path": "/tmp",
    "temp_filename": "/tmp/syncky.gz",
    "destination_database": "farivi_tpv_appfarivi",
    "q1": "update go_productos_existencia set existencias=10000;",
    "q2": "insert ignore into  go_productos_existencia ( producto_k, sucursal_k, existencias, limites_manuales, limite_maximo, limite_minimo, categoria_bcg, categoria_rotacion, costo_compra, ventas_cuenta, ventas_cantidad_mensual, tipo, tipo_cambio, tabla)  select p.producto_k, s.sucursal_k, 10000, 0, 0, 0, 0, null,"
          "null, null, null, null, null,null from go_productos p, go_sucursales s where s.activo=1 and p.activo=1;",
    "iweb": {
        "host": "198.50.124.199",
        "port": 22546,
        "user": "root",
        "password": "rVoywwu6a6LHZhZB4ETt",
        "temp_filename": "/tmp/syncky.gz",
        "source_database": "farivi_tpv_appfarivi",
    },
    "local_systems": [ {
        "name": "Casimiro Caja Respaldo",
        "host": "100.94.134.115",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Tlaxiaco Caja Respaldo",
        "host": "100.94.142.95",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Juxtlahuaca Caja Respaldo",
        "host": "100.76.183.135",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {

        "name": "Putla Caja Respaldo",
        "host": "100.117.1.81",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Huajuapan",
        "host": "100.127.197.5",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Casimiro",
        "host": "100.78.77.70",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "5 de Febrero",
        "host": "100.109.86.14",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Tlaxiaco",
        "host": "100.72.70.58",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Tlaxiaco Menudeo",
        "host": "100.108.79.88",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Putla",
        "host": "100.124.92.57",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Juxtlahuaca",
        "host": "100.107.230.50",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Juxtlahuaca Centro",
        "host": "100.67.161.102",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Mina",
        "host": "100.110.151.69",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }, {
        "name": "Nochixtlan",
        "host": "100.121.152.43",
        "user": "sistemas",
        "password": "Farivi%2022",
        "active": True,
    }]
}
