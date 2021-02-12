#!/bin/sh

# 189.45.136.111
# 192.168.1.4:10001

SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080

# TSserver.corenrj.local
REMOTE_IP=172.16.0.26
REMOTE_PORT=3389
REMOTE_WIDTH=880
REMOTE_HEIGHT=730
REMOTE_DOMAIN=CORENRJ
REMOTE_USER=willianbrito
REMOTE_PASSWORD=$(zenity --password)

IMPRIMIR_DIR=${HOME}/IMPRIMIR

REMOTE_X=$[${SCREEN_WIDTH}-${REMOTE_WIDTH}]

(
    while : ; do

        mkdir -p ${HOME}/REMOTO-NOVOS
        # TODO: FIXME: IR ALTERNANDO
        if : ; then

            xfreerdp \
                /t:INCORP \
                +clipboard \
                -themes \
                -decorations \
                -wallpaper \
                -mouse-motion \
                -fonts \
                /bpp:8 \
                /d:${REMOTE_DOMAIN} \
                /u:${REMOTE_USER} \
                /p:${REMOTE_PASSWORD} \
                /v:${REMOTE_IP}:${REMOTE_PORT} \
                /w:${REMOTE_WIDTH} \
                /h:${REMOTE_HEIGHT} \
                /window-position:${REMOTE_X}x0 \
                /drive:IMPRIMIR,${IMPRIMIR_DIR}
        else

            rdesktop -D -T INCORP ${REMOTE_IP}:${REMOTE_PORT} -g ${REMOTE_WIDTH}x${REMOTE_HEIGHT}+${REMOTE_X}+0 -u ${REMOTE_DOMAIN}\\${REMOTE_USER} -p ${REMOTE_PASSWORD} -r disk:IMPRIMIR=${IMPRIMIR_DIR} -M -a 8 -z -P -x m

        fi

        sleep 2

    done
) &
