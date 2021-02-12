#!/bin/python

import sys
import os
import socket
import time
import re
import cbor
import hashlib

IMPRESSORA_IP = '172.23.0.2'
IMPRESSORA_PORTA = 80

NOVOS_DIR     = '/home/speedyb0y/REMOTO-NOVOS'
IMPRESSOS_DIR = '/home/speedyb0y/REMOTO-IMPRESSOS'

DB = cbor.loads(open('.DB.cbor', 'rb').read())

# TODO: FIXME: SALVAR COMO INT
now = time.strftime(f'%Y-%m-%d %H:%M:%S')

deletar = []

# TODO: FIXME: REMOVER OS ARQUIVOS JÁ DELETADOS

for novoName in sorted(os.listdir(NOVOS_DIR)):

    ORIGINAL = f'{NOVOS_DIR}/{novoName}'

    # IGNORA CERTOS ARQUIVOS
    if novoName == 'teste.test':
        continue

    # IGNORA O QUE JÁ SABE QUE NÃO É PDF
    if novoName.lower().endswith(('.txt', '.jpg', '.bmp', '.doc', '.docx', '.ppt', '.exe', '.zip', '.msi', '.rar', '.html', '.htm')):
        continue

    # stat

    # TODO: FIXME: LIMITAR TAMANHO DO ARQUIVO
    hash_= open(ORIGINAL, 'rb').read()

    # IGNORA ARQUIVOS INCOMPLETOS
    if b'%%EOF' not in hash_[-128:]:
        continue

    hash_ = hashlib.sha256(hash_)
    hash_ = hash_.hexdigest()

    text = []
    fd = os.popen(f'pdftotext "{ORIGINAL}" -')
    while True:
        _ = os.read(fd.fileno(), 1024*1024*64)
        if not _:
            break
        text.append(_)
    fd.close()
    text = b''.join(text)

    #
    if b'atesta a situa\xc3\xa7\xc3\xa3o cadastral,' in text:
        tipo = 'CERTIDAO'
    else:
        tipo = ''

    if False:
        # EXTRAIR O NOME
        titularNome = 'NOME DO TITULAR'
    else:
        titularNome = ''

    del text

    # TODO: FIXME: TENTAR EXIBIR COM A DATA DO ARQUIVO EM SI, SE FOR CONHECIDA
    novoTime = 0

    DB[hash_] = (now, novoTime, novoName, tipo, titularNome)

    ## TODO: FIXME: ŚO SE TIVER SUCESSO
    os.system(f'pdftocairo -pdf "{ORIGINAL}" {IMPRESSOS_DIR}/{hash_}')

    deletar.append(ORIGINAL)

# SALVA DE FORMA ATÔMICA
open('.DB.cbor.tmp', 'wb').write(cbor.dumps(DB))

os.rename('.DB.cbor.tmp', '.DB.cbor')

#
for ORIGINAL in deletar:
    os.unlink(ORIGINAL)

for hash_ in selecionados = os.popen('zenity --list --text="SELECIONE OS ARQUIVOS A IMPRIMIR" --ok-label="IMPRIMIR" --modal --title="IMPRIMIR" --width=700 --height=500 --print-column=1 --hide-column=1 --column=HASH --column=DATA --column=TIPO --column=NOME --column=ARQUIVO --multiple --separator=" " ' +
    ' '.join(f'{hash_} "{adicionadoTime}" "{tipo}" "{titularNome}" "{novoName}"' for hash_, (adicionadoTime, novoTime, novoName, tipo, titularNome) in DB.items())
    ).read()[:-1].split():

    # TODO: FIXME: DEPENDENDO DO QUE FOR, COLOCAR FRENTE E VERSO

    try:
        MENSAGEM = (
            'Content-Disposition: form-data; name="OKIPAPERFEED"\r\n\r\nTRAY1\r\n'
            'Content-Disposition: form-data; name="COPIES"\r\n\r\n1\r\n'
            'Content-Disposition: form-data; name="COLLATE"\r\n\r\nfalse\r\n'
            'Content-Disposition: form-data; name="FITTOPAGE"\r\n\r\ntrue\r\n'
            'Content-Disposition: form-data; name="DUPLEX"\r\n\r\n0\r\n'
            'Content-Disposition: form-data; name="PAGESET"\r\n\r\nfalse\r\n'
            'Content-Disposition: form-data; name="FROMTO"\r\n\r\n\r\n'
            'Content-Disposition: form-data; name="PDFPASSWORD"\r\n\r\n\r\n'
            'Content-Disposition: form-data; name="PASSWORD"\r\n\r\n\r\n'
            'Content-Disposition: form-data; name="WLS_UPLOAD_FILE"; filename="Boleto.PDF"\r\n'
            'Content-Type: application/pdf\r\n'
            '\r\n').encode() + open(f'{IMPRESSOS_DIR}/{hash_}', 'rb').read()
    except: # TODO: FIXME: MENSAGEM DE ERRO AO FALHAR
        print('FALHOU')
        continue

    sock = socket.socket()
    sock.connect((IMPRESSORA_IP, IMPRESSORA_PORTA))
    sock.sendall((
        'POST /printer/print.cgi HTTP/1.1\r\n'
        f'Host: {IMPRESSORA_IP}\r\n'
        'Accept: */*\r\n'
        'Accept-Language: en-US,en;q=0.5\r\n'
        'Accept-Encoding: gzip, deflate\r\n'
        'Content-Type: multipart/form-data; boundary=---------------------------159599792230280882493265112558\r\n'
        f'Content-Length: {len(MENSAGEM)}\r\n'
        'Connection: keep-alive\r\n'
        '\r\n'
        ).encode() + MENSAGEM)

    while sock.recv(65536):
        pass

    sock.close()
