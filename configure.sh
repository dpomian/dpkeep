#!/bin/sh
PWD=`pwd`


setupVirtualenv() {
	echo "\n\nsetting up virtualenv..."

	virtualenv venv
	source $PWD/venv/bin/activate
	pip install -r $PWD/requirements.txt
	deactivate

	echo "done."
}

generateRunWebScript() {
	echo "\n\ngenerating runweb script..."

	runwebfile="$PWD/runweb.sh"
	echo "#!/bin/sh" > $runwebfile
	echo "source $PWD/venv/bin/activate" >> $runwebfile
	echo "cd $PWD/web" >> $runwebfile
	echo "python webapp.py" >> $runwebfile
	echo "deactivate" >> $runwebfile
	chmod +x $runwebfile

	echo "done."
}

generateNetrcFile() {
	echo "\n\ngenerating netrc file..."

  mkdir -p $PWD/res/prd
	netrcfile=$PWD/res/prd/.netrc
	touch $netrcfile && rm -rf $netrcfile && touch $netrcfile
	chmod 400 $netrcfile
	
	echo "done."
}

generateStorageFile() {
	echo "\n\ngenerating storage file..."

	storagefile=$PWD/res/prd/.mykeep_storage
	rm -rf $storagefile && touch $storagefile

	echo "done."
}

generateBackupStorage() {
	echo "\n\ngenerating backup storage file..."

	backupstoragefile=$PWD/res/prd/.keep_backup
	rm -rf $backupstoragefile && touch $backupstoragefile
	chmod 400 $backupstoragefile

	echo "done."
}

generateBackupScript() {
	echo "\n\ngenerating backup script..."

	backupfile="$PWD/backup.sh"
	echo "#!/bin/sh" > $backupfile
	echo "BKP=\"$PWD/res/prd/.keep_backup\"" >> $backupfile
	echo "NETRC=\"$PWD/res/prd/.netrc\"" >> $backupfile
	echo "STORAGE=\"$PWD/res/prd/.mykeep_storage\"" >> $backupfile
	echo "if test -f \"\$BKP\"; then" >> $backupfile
	echo "  chmod +w \$BKP" >> $backupfile
	echo "fi" >> $backupfile
	echo "echo \`date\` >> \$BKP" >> $backupfile
	echo "cat \$NETRC >> \$BKP" >> $backupfile
	echo "echo >> \$BKP" >> $backupfile
	echo "cat \$STORAGE >> \$BKP" >> $backupfile
	echo "echo >> \$BKP" >> $backupfile
	echo "chmod 400 \$BKP" >> $backupfile
	chmod +x $backupfile

	echo "done."
}


generateRunnerScript() {
	echo "\n\ngenerating runner script..."

	runnerscript=$PWD/keep.sh
	echo "#!/bin/sh" > $runnerscript
	echo "source $PWD/venv/bin/activate" >> $runnerscript
	echo "python $PWD/cli/mykeep.py \"\$@\"" >> $runnerscript
	echo "deactivate" >> $runnerscript
	chmod +x $runnerscript

	echo "done."
}

setupVirtualenv
generateRunWebScript
generateNetrcFile
generateStorageFile
generateBackupStorage
generateBackupScript
generateRunnerScript

echo "\n\nConfiguration Done"
echo "\n/!\\ Don't forget to add your password in $PWD/res/prd/.netrc file /!\\"
