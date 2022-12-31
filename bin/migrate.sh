#!/bin/bash

# Migrate from csv data to sqlite + add epoch


if [[ -z "$1" || -z "$2" ]]

    then

        echo -e "Usage: migrate.sh file_CSV file_SQLITE"
        exit 1

fi

IFS=$'\t\n'

for entry in $(cat "$1")

    do

        data=`echo "$entry" | awk -F "," '{print $1}'`
        temp=`echo "$entry" | awk -F "," '{print $2}'`
        epoch=`echo "$data" | xargs -d \n date +%s -d`
        sqlite3 "$2" 'insert into temperature values("'$data'", '$epoch', '$temp');'

done

