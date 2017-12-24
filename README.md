i3msg-python
===
A minimal Python interface to the [i3wm](https://i3wm.org/) [IPC](https://i3wm.org/docs/ipc.html).

About
---
[i3wm](https://i3wm.org/) can be controlled through commands sent to its IPC socket. `i3-msg` facilitates this through the command line.  
i3msg-python lets you do the same (and more) from Python.

i3msg-python is a simple wrapper for i3wm's raw IPC command interface. It lets you trivially issue [commands](https://i3wm.org/docs/userguide.html#_list_of_commands) or [other messages](https://i3wm.org/docs/ipc.html#_sending_messages_to_i3) or [subscribe to events](https://i3wm.org/docs/ipc.html#_events) without having to bother with socket communication, sanity checking or the internal IPC protocol. It consists of a ~50 line Python script and is fully portable.

Installation
---
i3msg is on [PyPi](https://pypi.python.org/pypi/i3msg):
```Bash
pip install i3msg
```

Alternatively, you can download and put it where you need it:
```Bash
cd /path/to/dependent/script.py
wget https://github.com/ceryn/i3msg-python/i3msg.py
touch __init__.py
```

Alternatively, you can download it to somewhere like above and add that folder to your python path:
```Bash
echo 'export PYTHONPATH="/path/to/your/python/scripts/:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
```

Usage
---
To send a message do `i3msg.send(i3msg.NAME_OF_MESSAGE, argument_if_any)`,  
where `NAME_OF_MESSAGE` is the [name of the message](https://i3wm.org/docs/ipc.html#_sending_messages_to_i3) you want to send and the argument is whichever argument your message type requires. If your message type does not require an argument you can omit it and just specify the message name.

To subscribe to an event do `i3msg.subscribe(['name_of_event1', 'name_of_event2'], name_of_event_handler)`,  
where the first argument is a list of one or more strings of [names of the events](https://i3wm.org/docs/ipc.html#_available_events) you want to subscribe to and the second argument is the name of your function to be called whenever the event occurs.  
Your specified event handler must accept two arguments:
* `event`, which is the type of the event that triggered your handler function, and 
* `data`, which is the relevant event data returned by i3wm as a Python object, usually a dictionary.

Examples
---
Focus the container to the right, just like you would do with `i3-msg`:
```Python
import i3msg as i3

i3.send(i3.RUN_COMMAND, 'focus right')
```

Print name of current workspace:
```Python
import i3msg as i3

wss = i3.send(i3.GET_WORKSPACES)
for ws in wss:
    if ws['focused']:
        print ws['name']
```

Subscribe to relevant events to print names of workspaces and windows as they are focused:
```Python
import time, i3msg as i3

def focus_changed_handler(event, data):
    if event == i3.workspace:
        if data['change'] == 'focus':
            print 'Workspace changed to: %s' % data['current']['name']
    elif event == i3.window:
        if data['change'] == 'focus':
            print 'Window changed to: %s' % data['container']['name']

i3.subscribe(['workspace', 'window'], focus_changed_handler)

# Sleep forever while the daemon thread is listening for events.
while True:
    time.sleep(1)
```

Contributing
---
Contributions are very welcome.  
You can reach out with your ideas/requests/improvements on Freenode IRC (Ceryn, #i3) or here.
