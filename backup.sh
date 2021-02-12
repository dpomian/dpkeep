#!/bin/sh
BKP="/Users/dpomian/hardwork/pywork/dpkeep/.keep_backup"
NETRC="/Users/dpomian/hardwork/pywork/dpkeep/res/prd/.netrc"
STORAGE="/Users/dpomian/hardwork/pywork/dpkeep/res/prd/.mykeep_storage"

if test -f "$BKP"; then
	chmod +w $BKP
fi

echo `date` >> $BKP
cat $NETRC >> $BKP
echo "\n" >> $BKP
cat $STORAGE >> $BKP
echo "\n" >> $BKP
chmod 400 $BKP
