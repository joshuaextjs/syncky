# #!/bin/bash
# Description: Elimina todo el stack de pandora incluyendo los volúmenes
# Author: Miguel Salas
# -------------------------------------------------

read -p "Deseas eliminar completamente SYNCKY?. Se eliminarán contenedores y redes (yes/no) " yn

case $yn in 
	yes ) echo Eliminando Syncky...;
    ##############################
    # SYNCKY CORE
    ##############################

    # Se eliminan los contenedores
    docker compose down -v

    echo Eliminación completada;
    exit;;
	no ) echo Bytes...;
		exit;;
	* ) echo Respuesta inválida;
		exit 1;;
esac

