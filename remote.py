#!/user/bin/python

import sys
import os
import time

def pipe (cmd):

    r, w = os.pipe()

    if not os.fork():
        os.close(1)
        os.close(r)
        os.dup2(w, 1)
        os.system(cmd)
        exit(0)

    os.close(w)

    # TODO: FIXME: KEEP READING
    x = os.read(r, 128*1024*1024)[:-1]

    os.close(r)

    return x

# TSserver.corenrj.local
remoteIP='172.16.0.26'
remotePort = 3389
remoteWidth = 880
remoteHeight = 730
remoteDomain = 'CORENRJ'
remoteUser = 'willianbrito'
remotePwd = pipe('zenity --password').decode()

printDir = './IMPRIMIR'

assert isinstance(printDir, str) and printDir
assert isinstance(remoteIP, str) and remoteIP
assert isinstance(remoteDomain, str)
assert isinstance(remoteUser, str) and remoteUser
assert isinstance(remotePwd, str) and remotePwd
assert isinstance(remotePort, int) and 0 <= remotePort <= 0xFFFF
assert 100 <= remoteWidth <= 20000
assert 100 <= remoteHeight <= 20000

while True:

    os.system(f'mkdir -p {printDir}')

    # TODO: FIXME: AUTO DISCOVER IT
    screenWidth = 1920
    screenHeight = 1080

    remoteX = screenWidth - remoteWidth

    # TODO: FIXME: IR ALTERNANDO
    if True:

        os.system('xfreerdp'
            '/t:INCORP '
            '+clipboard '
            '-themes '
            '-decorations '
            '-wallpaper '
            '-mouse-motion '
            '-fonts '
            '/bpp:8 '
            f'/d:{remoteDomain} '
            f'/u:{remoteUser} '
            f'/p:{remotePwd} '
            f'/v:{remoteIP}:{remotePort} '
            f'/w:{remoteWidth} '
            f'/h:{remoteHeight} '
            f'/window-position:{remoteX}x0 '
            f'/drive:IMPRIMIR,{printDir} '
            )
    else:

        os.system(f'rdesktop -D -T INCORP {remoteIP}:{remotePort} -g {remoteWidth}x{remoteHeight}+{remoteX}+0 -u {remoteDomain}\\{remoteUser} -p {remotePwd} -r disk:IMPRIMIR={printDir} -M -a 8 -z -P -x m')

    time.sleep(2)
