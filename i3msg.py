#!/usr/bin/env python
#https://github.com/Ceryn/i3msg-python
import socket, subprocess, struct, json, threading

MSGS = ['RUN_COMMAND', 'GET_WORKSPACES', 'SUBSCRIBE', 'GET_OUTPUTS', 'GET_TREE', 'GET_MARKS', 'GET_BAR_CONFIG', 'GET_VERSION', 'GET_BINDING_MODES', 'GET_CONFIG']
EVENTS = ['workspace', 'output', 'mode', 'window', 'barconfig_update', 'binding', 'shutdown']
for i, v in enumerate(MSGS):
    vars()[v] = i
for i, v in enumerate(EVENTS):
    vars()[v] = i
i3sock = None

def get_i3sock():
    global i3sock
    if i3sock is None:
        i3sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        i3sock.connect(subprocess.check_output(['i3', '--get-socketpath']).strip())
    return i3sock

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
    s = get_i3sock()
    s.send(encode(n, str(msg)))
    _, data = recvall(s)
    return json.loads(data)

def handle_subscription(s, handler):
    while True:
        event, data = recvall(s)
        handler(event, json.loads(data))

def subscribe(events, handler):
    s = get_i3sock()
    s.send(encode(SUBSCRIBE, json.dumps(events)))
    _, data = recvall(s)
    data = json.loads(data)
    if not data.has_key('success') or data['success'] != True:
        raise Exception('Subscription failed, got data: %s' % data)
    t = threading.Thread(target=handle_subscription, args=(s, handler))
    t.daemon = True
    t.start()
