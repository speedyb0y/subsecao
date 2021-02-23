#!/user/bin/python

import sys
import os
import time
import fcntl

# echo $[2*1024*1024*1024] > /proc/sys/fs/pipe-max-size || exit 1
# echo $[2*1024*1024*1024] > /proc/sys/fs/pipe-user-pages-hard || exit 1
# echo $[2*1024*1024*1024] > /proc/sys/fs/pipe-user-pages-soft || exit 1

F_SETPIPE_SZ = 1031
F_GETPIPE_SZ = 1032

def pipe (buffSize, cmd):

    r, w = os.pipe()

    fcntl.fcntl(r,  F_SETPIPE_SZ, buffSize)

    assert int(fcntl.fcntl(r,  F_GETPIPE_SZ)) == buffSize

    pid = os.fork()

    if not pid:
        os.close(1)
        os.close(r)
        os.dup2(w, 1)
        os.system(cmd)
        exit(0)

    os.close(w)

    _, status = os.waitpid(pid, 0)

    assert _ == pid
    assert status == 0

    data = os.read(r, buffSize)

    os.close(r)

    return data

# TSserver.corenrj.local
remoteHost ='172.16.0.26'
remotePort = 3389
remoteWidth = 880
remoteHeight = 730
remoteDomain = 'CORENRJ'
remoteUser = 'willianbrito'
remotePwd = pipe(4096, 'zenity --password')[:-1].decode()

printDir = './IMPRIMIR'

assert isinstance(printDir, str) and printDir
assert isinstance(remoteHost, str) and remoteHost
assert isinstance(remotePort, int) and 0 <= remotePort <= 0xFFFF
assert isinstance(remoteDomain, str)
assert isinstance(remoteUser, str) and remoteUser
assert isinstance(remotePwd, str) and remotePwd
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

        os.system('xfreerdp '
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
            f'/v:{remoteHost}:{remotePort} '
            f'/w:{remoteWidth} '
            f'/h:{remoteHeight} '
            f'/window-position:{remoteX}x0 '
            f'/drive:IMPRIMIR,{printDir} '
            )
    else:

        os.system(f'rdesktop -D -T INCORP {remoteHost}:{remotePort} -g {remoteWidth}x{remoteHeight}+{remoteX}+0 -u {remoteDomain}\\{remoteUser} -p {remotePwd} -r disk:IMPRIMIR={printDir} -M -a 8 -z -P -x m')

    time.sleep(2)
