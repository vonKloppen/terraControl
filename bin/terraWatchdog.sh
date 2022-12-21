#!/bin/bash



statusFile="/var/log/terraControl.status"
checkInterval=20

if [[ -f "$statusFile" ]]

	then

		touch "$statusFile"	
		echo "0" > "$statusFile"

fi

while true

	do

		failedChecks=`head -n1 "$statusFile"`

		if [[ "$failedChecks" -ge 2 ]]

			then

				systemctl restart terraControl.service
				failedChecks=0
				echo "$failedChecks" > "$statusFile"
				sleep 5

		fi

		check=`systemctl is-active terraControl.service`

		if [[ "$check" != "active" ]]

			then

				failedChecks=$(("$failedChecks"+1))
				echo -e "$failedChecks" > "$statusFile"

			else

				echo "0" > "$statusFile"

		fi

		sleep "$checkInterval"

	done

