#!/bin/bash

PYTHONPATH=$PWD:$PWD/..${PYTHONPATH:+:$PYTHONPATH}
export PYTHONPATH

ALL="core"

if [ $# -eq 0 ]; then
	TYPES=$ALL
elif [ $1 == '-h' ]; then
	echo "Valid arguments are: $ALL"
else
	TYPES=$@
fi

for type in $TYPES; do
	echo "** $type **"
	django-admin.py test $type --settings=settings_$type
	echo; echo
done
