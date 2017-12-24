#!/usr/bin/env python
#https://github.com/Ceryn/i3msg-python
import socket, subprocess, struct, json, threading

MSGS = ['RUN_COMMAND', 'GET_WORKSPACES', 'SUBSCRIBE', 'GET_OUTPUTS', 'GET_TREE', 'GET_MARKS', 'GET_BAR_CONFIG', 'GET_VERSION', 'GET_BINDING_MODES', 'GET_CONFIG']
EVENTS = ['workspace', 'output', 'mode', 'window', 'barconfig_update', 'binding', 'shutdown']
for k, v in zip(MSGS, range(len(MSGS))) + zip(EVENTS, range(len(EVENTS))):
    vars()[k] = v

def encode(n, msg=''):
    return 'i3-ipc' + struct.pack('I', len(msg)) + struct.pack('I', n) + msg

def decode(blob):
    size = int(struct.unpack('I', blob[ 6:10])[0])
    type = int(struct.unpack('I', blob[10:14])[0]) & 0x7fffffff
    return size, type, blob[14:]

def recvall(s):
    size, event, data = decode(s.recv(14))
    while len(data) < size:
        data += s.recv(size - len(data))
    return event, data

def send(n, msg=''):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(subprocess.check_output(['i3', '--get-socketpath']).strip())
    s.send(encode(n, str(msg)))
    _, data = recvall(s)
    s.close()
    return json.loads(data)

def handle_subscription(s, handler):
    while True:
        event, data = recvall(s)
        handler(event, json.loads(data))

def subscribe(events, handler):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(subprocess.check_output(['i3', '--get-socketpath']).strip())
    s.send(encode(SUBSCRIBE, json.dumps(events)))
    _, data = recvall(s)
    data = json.loads(data)
    if not data.has_key('success') or data['success'] != True:
        raise Exception('Subscription failed, got data: %s' % data)
    t = threading.Thread(target=handle_subscription, args=(s, handler))
    t.daemon = True
    t.start()