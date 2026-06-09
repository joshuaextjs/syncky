#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Optional

import ecs_logging

import ipaddress
import macaddress

import winrm
import typer

logger = logging.getLogger("remote_cmd")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/syncky/logs/remote_cmd.log')
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)


sucursales = [{
    "name": "Casimiro",
    "ip_address": "192.168.102.100",
    "user": "sistemas",
    "password": "Farivi%2022",
    "pu_ip_address": "192.168.102.101",
    "pu_mac_address": "581122C91E26",
    "pu_subnet_mask": "255.255.255.0",
    "pu_port": 7
}, {
    "name": "Tlaxiaco",
    "ip_address": "192.168.104.100",
    "user": "sistemas",
    "password": "Farivi%2022",
    "pu_ip_address": "192.168.104.101",
    "pu_mac_address": "581122C91E9D",
    "pu_subnet_mask": "255.255.255.0",
    "pu_port": 7
}, {
    "name": "Juxtlahuaca Centro",
    "ip_address": "192.168.108.100",
    "user": "sistemas",
    "password": "Farivi%2022",
    "pu_ip_address": "192.168.108.101",
    "pu_mac_address": "581122C91E92",
    "pu_subnet_mask": "255.255.255.0",
    "pu_port": 7
}]


def validate_mac_address(mac_address):
    try:
        macaddress.MAC(mac_address)
    except ValueError:
        return False

    return True


def validate_ip_address(ip_address):
    try:
        _ = ipaddress.ip_address(ip_address)
    except ValueError:
        return False

    return True


"""
def validate(ip_address: str):
    if not validate_ip_address(ip_address):
        typer.echo("IP address {} is not valid".format(ip_address))
        return False

    if not validate_mac_address(dst_mac):
        typer.echo("MAC address {} is not valid".format(dst_mac))
        return False
"""

app = typer.Typer(help="Ejecución de comandos de forma remota en equipos windows a través de WinRM.")


@app.command()
def remote_execute(cmd: Optional[str] = None, ip_address: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, output: Optional[bool] = False):

    if validate_ip_address(ip_address):
        try:
            logger.debug("Connecting...", extra={'destination.ip_address': ip_address})
            sess = winrm.Session(ip_address, auth=(user, password))
            resp = sess.run_cmd(cmd)
            logger.debug("CMD: {}".format(cmd), extra={'destination.ip_address': ip_address})

            if resp.status_code == 0:
                logger.info("{}".format(resp.std_out), extra={'destination.ip_address': ip_address})
            else:
                logger.error("{}".format(resp.std_out), extra={'destination.ip_address': ip_address})

            if output:
                typer.echo("{}".format(resp.std_out))

        except Exception as e:
            logger.error("Ooop, something wrong".format(e), extra={'destination.ip_address': ip_address})


@app.command()
def power_on(pu_ip_address: Optional[str] = None, pu_mac_address: Optional[str] = None,
            pu_subnet_mask: Optional[str] = None, pu_port: Optional[int] = None, ip_address: Optional[str] = None,
            user: Optional[str] = None, password: Optional[str] = None):

    if validate_ip_address(pu_ip_address) :

        cmd = "C:\\wolcmd.exe {} {} {} {}".format(pu_mac_address, pu_ip_address, pu_subnet_mask, pu_port)
        remote_execute(cmd, ip_address, user, password, True)


@app.command()
def power_off(ip_address: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
    cmd = "shutdown -s"
    remote_execute(cmd, ip_address, user, password, True)


@app.command()
def farivi_power_on():
    for sucursal in sucursales:
        power_on(sucursal["pu_ip_address"], sucursal["pu_mac_address"], sucursal["pu_subnet_mask"],
                 sucursal["pu_port"], sucursal["ip_address"], sucursal["user"], sucursal["password"])


@app.command()
def farivi_power_off():
    for sucursal in sucursales:
        power_off(sucursal["pu_ip_address"], sucursal["user"], sucursal["password"])


# Start program
if __name__ == "__main__":
    app()

