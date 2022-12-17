#!/bin/bash



reportFile="/var/log/terraControl.log"
checkInterval=20

if [[ -f "$reportFile" ]]

	then

		touch /var/log/terraControl.log	
		echo "0" > "$reportFile"

fi

while true

	do

		failedChecks=`head -n1 "$reportFile"`

		if [[ "$failedChecks" -ge 2 ]]

			then

				systemctl restart terraControl.service
				failedChecks=0
				echo "$failedChecks" > "$reportFile"
				sleep 5

		fi

		check=`systemctl is-active terraControl.service`

		if [[ "$check" != "active" ]]

			then

				failedChecks=$(("$failedChecks"+1))
				echo -e "$failedChecks" > "$reportFile"

			else

				echo "0" > "$reportFile"

		fi

		sleep "$checkInterval"

	done

