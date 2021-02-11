#!/bin/sh
BKP="./.keep_backup"
NETRC="./res/prd/.netrc"
STORAGE="./res/prd/.mykeep_storage"

if test -f "$BKP"; then
	chmod +w $BKP
fi

echo `date` >> $BKP
cat $NETRC >> $BKP
echo "\n" >> $BKP
cat $STORAGE >> $BKP
echo "\n" >> $BKP
chmod 400 $BKP
