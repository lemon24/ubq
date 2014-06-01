#!/bin/bash

PID=$( pgrep -f 'python3 ubq.py' )

if [ "$?" != "0" ]; then
    echo ubq process not found
    echo starting ubq...
    cd "$( dirname $0 )"
    python3 ubq.py
else
    echo ubq process found with pid $PID
    echo sending SIGUSR1...
    kill -s SIGUSR1 $PID
fi
