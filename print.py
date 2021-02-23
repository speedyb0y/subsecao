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

# TODO: FIXME: FULL PATH
NOVOS_DIR     = 'IMPRIMIR'
IMPRESSOS_DIR = 'IMPRESSO'

DB = cbor.loads(open('.DB.cbor', 'rb').read())

# TODO: FIXME: SALVAR COMO INT
now = time.strftime(f'%Y-%m-%d %H:%M:%S')

deletar = []

# TODO: FIXME: REMOVER OS ARQUIVOS JÁ DELETADOS

# TODO: FIXME: DAEMONIZAR, E USAR UM PAUSE() E EXECUTAR COM SIGNALS

for novo in sorted(os.listdir(NOVOS_DIR)):

    ORIGINAL = f'{NOVOS_DIR}/{novo}'

    # IGNORA O QUE JÁ SABE QUE NÃO É PDF
    if novo.lower().endswith(('.txt', '.jpg', '.bmp', '.doc', '.docx', '.ppt', '.exe', '.zip', '.msi', '.rar', '.html', '.htm', '.test')):
        continue

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

    # TODO: FIXME: SOBRESCREVER COM A DATA DO ARQUIVO? :/
    # NÃO, MELHOR CONSIDERAR A DATA EM QUE *NÓS* TRABALHAMOS COM O ARQUIVO
    # OU ENTÃO, MANTER AMBAS AS DATAS

    inscricao = tipo = nome = ''
    timestamp = now
    detalhe = novo

    # TODO: FIXME: BOLETOS E VENCIMENTO
    # TODO: FIXME: ESPELHOS
    # TODO: FIXME: TERMOS DE PARCELAMENTO
    # TODO: FIXME: REQUERIMENTOS
    # TODO: FIXME: FIXAS DE QUALIFICAÇÃO
    if b'atesta a situa\xc3\xa7\xc3\xa3o cadastral,' in text:

        tipo = 'CERTIDAO'

        try:
            nome = re.findall(b'Nome: ([^\n]*)', text)[0].decode()
        except:
            pass

        try:
            inscricao = re.findall(b'Inscri\xc3\xa7\xc3\xa3o: ([^\n]*)', text)[0].decode()
        except:
            pass

        # TODO: FIXME: SITUAÇÃO
        detalhe = ''

        # TENTA USAR A DATA DA CERTIDÃO EM SI
        try:
            day, _, hours = re.findall(b'emitida em ([^.]*)', text)[0].split()
            day, month, year, hours, mins, secs = map(int, (*day.split(b'/'), *hours.split(b':')))
            timestamp = '%04d-%02d-%02d %02d:%02d:%02d' % (year, month, day, hours, mins, secs)
        except:
            pass

    del text

    DB[hash_] = (timestamp, nome, inscricao, tipo, detalhe)

    ## TODO: FIXME: ŚO SE TIVER SUCESSO
    os.system(f'pdftocairo -pdf "{ORIGINAL}" {IMPRESSOS_DIR}/{hash_}')

    deletar.append(ORIGINAL)

# SALVA DE FORMA ATÔMICA
open('.DB.cbor.tmp', 'wb').write(cbor.dumps(DB))

os.rename('.DB.cbor.tmp', '.DB.cbor')

#
for ORIGINAL in deletar:
    os.unlink(ORIGINAL)

for hash_ in os.popen('zenity --list --text="SELECIONE OS ARQUIVOS A IMPRIMIR" --ok-label="IMPRIMIR" --modal --title="IMPRIMIR" --width=900 --height=700 --print-column=1 --hide-column=1 --column=HASH --column=DATA --column=NOME --column=INSCRICAO --column=TIPO --column= --multiple --separator=" " ' +
    ' '.join(f'{hash_} "{adicionadoTime}" "{nome}" "{inscricao}" "{tipo}" "{novo}"' for hash_, (adicionadoTime, nome, inscricao, tipo, novo) in DB.items())
    ).read()[:-1].split():

    # TODO: FIXME: DEPENDENDO DO QUE FOR, COLOCAR FRENTE E VERSO
    # DEMAIS TIPOS, PERGUNTAR

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
    except FileNotFoundError: # TODO: FIXME: MENSAGEM DE ERRO AO FALHAR
        print('FALHOU')
        continue

    MENSAGEM = ('POST /printer/print.cgi HTTP/1.1\r\nContent-Type: multipart/form-data; boundary=@@@\r\n'
        f'Host: {IMPRESSORA_IP}\r\n'
        f'Content-Length: {len(MENSAGEM)}\r\n'
        '\r\n'
        ).encode() + MENSAGEM

    sock = socket.socket()
    sock.connect((IMPRESSORA_IP, IMPRESSORA_PORTA))
    sock.sendall(MENSAGEM)

    del MENSAGEM

    while sock.recv(65536):
        pass

    sock.close()
