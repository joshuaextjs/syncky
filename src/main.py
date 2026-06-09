    #!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import ecs_logging

from conf import syncky_conf

from queue import Queue
import threading

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from ftplib import FTP, FTP_TLS
from pathlib import Path

import winrm

logger = logging.getLogger("syncky")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/syncky/logs/syncky.log')
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)


class Syncky(object):
    """Syncky

    Sincronización de sistemas locales de Farivi
    """

    def __init__(self):
        logger.debug("Starting")
        self.main()
        logger.debug("Done")

    @staticmethod
    def crear_sesion_winrm(host, username, password):
        # intento 1: método antiguo (producción actual)
        try:
            sess = winrm.Session(host, auth=(username, password))
            r = sess.run_cmd('hostname')
            if r.status_code == 0:
                return sess
        except Exception as e:
            logger.debug(f"{host} legacy winrm fallo: {e}")

        # intento 2: método extendido (para nuevas sucursales)
        try:
            sess = winrm.Session(
                f'http://{host}:5985/wsman',
                auth=(username, password),
                transport='ntlm',
                message_encryption='auto',
                server_cert_validation='ignore',
            )
            r = sess.run_cmd('hostname')
            if r.status_code == 0:
                return sess
        except Exception as e:
            logger.debug(f"{host} ntlm winrm fallo: {e}")

        raise Exception(f"No se pudo conectar por WinRM a {host}")

    @staticmethod
    def update_products(sucursal, host, username, password, destination_database, q1, q2):
        try:
            logger.debug("Actualizando productos", extra={'workspace': sucursal})

            sess = Syncky.crear_sesion_winrm(host, username, password) # winrm.Session(host, auth=(username, password))
            resp = sess.run_cmd("C:\\wamp64\\bin\\mysql\\mysql8.3.0\\bin\\mysql.exe -uroot " + destination_database +
                                " -e \"" + q1 + "\"")

            if resp.status_code != 0:
                logger.error(str(resp.std_err, encoding='utf-8'), extra={'workspace': sucursal})
                return False

            resp = sess.run_cmd("C:\\wamp64\\bin\\mysql\\mysql8.3.0\\bin\\mysql.exe -uroot " + destination_database +
                                " -e \"" + q2 + "\"")

            if resp.status_code != 0:
                logger.error(str(resp.std_err, encoding='utf-8'), extra={'workspace': sucursal})
                return False
        except Exception as e:
            return False

        return True

    @staticmethod
    def load_backup(sucursal, host, username, password, destination_database):
        try:
            logger.debug("Importando respaldo", extra={'workspace': sucursal})
            
            sess = Syncky.crear_sesion_winrm(host, username, password) # winrm.Session(host, auth=(username, password))
            resp = sess.run_cmd("C:\\wamp64\\bin\\mysql\\mysql8.3.0\\bin\\mysql.exe -uroot " + destination_database +
                                " < C:\\syncky")
            
            if resp.status_code != 0:
                logger.error(str(resp.std_err, encoding='utf-8'), extra={'workspace': sucursal})
                return False

        except Exception as e:            
            logger.error(str(e), extra={'workspace': sucursal})
            return False
        
        return True

    @staticmethod
    def unzip_backup(sucursal, host, username, password):
        try:
            logger.debug("Descomprimiendo respaldo", extra={'workspace': sucursal})            

            sess =  Syncky.crear_sesion_winrm(host, username, password) # winrm.Session(host, auth=(username, password))
            resp = sess.run_cmd(""""C:\\Program Files\\7-Zip\\7z.exe" x C:\\syncky.gz -oC:\\ -y""")

            if resp.status_code != 0:
                logger.error(str(resp.std_err, encoding='utf-8'), extra={'workspace': sucursal})                
                return False
            
        except Exception as e:
            logger.error(str(e), extra={'workspace': sucursal})
            return False
        return True

    @staticmethod
    def upload_backup(sucursal, host, username, password, temp_filename):

        """ Sube el gzip del backup a una sucursal utiliza el FileZilla Server de los equipos """

        try:
            logger.debug("Subiendo respaldo", extra={'workspace': sucursal})            

            with FTP(host, username, password) as ftp, open(temp_filename, "rb") as file:
                ftp.storbinary(f"STOR {temp_filename.name}", file)

        except Exception as e:
            logger.error(str(e), extra={'workspace': sucursal})
            return False
        
        return True

    def get_backup(
        self,
        source_ip,
        source_port,
        source_username,
        source_password,
        source_database,
        temp_filename,
        temp_path,
    ):

        """ Genera el backup de las 5 tablas y lo comprime en gzip """        

        cmd = (
            "rm -rf "
            + temp_filename
            + "&& mysqldump --skip-triggers --databases " + source_database +
            " --tables go_clientes go_productos go_productos_precios go_usuarios go_usuarios_sucursal go_productos_promociones | "
            "gzip -9 -c > "
            + temp_filename
        )

        try:
            logger.debug("Generando respaldo", extra={'workspace': 'iWeb'})       

            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(
                hostname=source_ip,
                port=source_port,
                username=source_username,
                password=source_password,
                look_for_keys=False,
                timeout=10,
            )
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()

        except Exception as e:

            logger.error(str(e), extra={'workspace': 'iWeb'})            

            return False

        """ Descarga el gzip del backup utilizando SSH """

        try:
            logger.debug("Descargando respaldo", extra={'workspace': 'iWeb'})

            scp = SCPClient(ssh.get_transport())
            scp.get(remote_path=temp_filename, local_path=temp_path)
            scp.close()

        except Exception as e:
            logger.error(str(e), extra={'workspace': 'iWeb'})
            return False

        return True

    def sync_local_system(self, queue, semaphore):

        data = queue.get()

        if self.upload_backup(data["sucursal"],data["host"],data["user"],data["password"], data["temp_filename"]):
            if self.unzip_backup(data["sucursal"], data["host"], data["user"], data["password"]):
                if self.load_backup(data["sucursal"], data["host"], data["user"], data["password"],
                                     data["destination_database"]):
                    if self.update_products(data["sucursal"], data["host"], data["user"], data["password"],
                                            data["destination_database"], data["q1"], data["q2"]):
                        logger.info("Sincronización completa", extra={'workspace': data['sucursal'],
                                                                      'syncky_success': True})

        semaphore.release()
        queue.task_done()  

    def sync_local_systems(self, local_systems, temp_filename, destination_database, q1, q2):

        queue = Queue()
        semaphore = threading.Semaphore(len(local_systems))

        for local_system in local_systems:

            if local_system["active"]:

                queue.put({
                    'sucursal': local_system["name"],
                    'host': local_system["host"], 
                    'user': local_system["user"], 
                    'password': local_system["password"], 
                    'temp_filename': temp_filename,
                    'destination_database': destination_database,
                    'q1': q1,
                    'q2': q2
                })

                semaphore.acquire()
                
                t = threading.Thread(target=self.sync_local_system, args=[queue, semaphore], daemon=True)

                t.start()

        queue.join()                              

    def main(self):

        if self.get_backup(
            syncky_conf['iweb']['host'],
            syncky_conf['iweb']['port'],
            syncky_conf['iweb']['user'],
            syncky_conf['iweb']['password'],
            syncky_conf['iweb']['source_database'],
            syncky_conf['iweb']['temp_filename'],
            syncky_conf['temp_path']            
        ):        
            self.sync_local_systems(
                syncky_conf['local_systems'],
                Path(syncky_conf['temp_filename']),
                syncky_conf['destination_database'],
                syncky_conf['q1'],
                syncky_conf['q2']
            )


# Start program
if __name__ == "__main__":
    s = Syncky()
