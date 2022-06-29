#!/bin/bash

if [ "$1" == "initdb" ]; then
    cd helper 
    python dbCreate.py
    echo "Database created"
    ls
elif [ "$1" == "deletedb" ]; then
    rm db.sqlite
    echo "Database deleted"
    ls
elif [ "$1" == "rebuild" ]; then
    rm db.sqlite
    echo "Database deleted"
    ls
    cd helper 
    python dbCreate.py
    echo "Database created"
    ls
else
    echo "initdb - создаст пустую бд"
    echo "deletedb - удалит бд"
    echo "rebuild - пересоберет бд"
fi
