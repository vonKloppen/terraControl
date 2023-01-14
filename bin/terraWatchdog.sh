#!/bin/bash

### Initial values

failedChecks=0

### VARIABLES

checkInterval=20
checkFailTreshold=3

logTAG="terraWatchdog"

controlService="terraControl.service"


while true

	do

		check=`systemctl is-active "$controlService"`

		if [[ "$check" != "active" ]]

			then

				failedChecks=$(("$failedChecks"+1))

				if [[ "$failedChecks" -ge "$checkFailTreshold" ]]

					then

						logger -t "$logTAG" "terraControl check failed "$checkFailTreshold" times. Restarting service.."
						systemctl restart "$controlService"


					else

						logger -t "$logTAG" "terraControl check failed. Count="$failedChecks""

				fi

			else

				if [[ "$failedChecks" != 0 ]]

					then

						logger -t "$logTAG" "terraControl is working again"

				fi

				failedChecks=0

		fi

		sleep "$checkInterval"

	done

