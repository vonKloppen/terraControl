#!/usr/bin/env bash

### Initial values

serviceFailedChecks=0
networkFailedChecks=0

### VARIABLES

checkInterval=20
serviceFailTreshold=3
networkFailTreshold=9

logTAG="terraWatchdog"

controlService="terraControl.service"
networkHostCheck="__IP_OR_HOSTNAME__"


while true

	do

		serviceCheck=`systemctl is-active "$controlService"`

		if [[ "$serviceCheck" != "active" ]]

			then

				serviceFailedChecks=$(("$serviceFailedChecks"+1))

				if [[ "$serviceFailedChecks" -ge "$serviceFailTreshold" ]]

					then

						logger -t "$logTAG" "terraControl service check failed "$serviceFailedChecks" times. Restarting service.."
						systemctl restart "$controlService"


					else

						logger -t "$logTAG" "terraControl check failed. Count="$serviceFailedChecks""

				fi

			else

				if [[ "$serviceFailedChecks" != 0 ]]

					then

						logger -t "$logTAG" "terraControl is working again"

				fi

				serviceFailedChecks=0

		fi

		ping -qc3 "$networkHostCheck" &>/dev/null

		if [[ "$?" -ne 0 ]]

			then

				networkFailedChecks=$(("$networkFailedChecks"+1))

				if [[ "$networkFailedChecks" -ge "$networkFailTreshold" ]]

					then

						logger -t "$logTAG" "terraControl network check failed "$networkFailTreshold" times. Restarting system.."
						reboot


                                        else

                                                logger -t "$logTAG" "terraControl network check failed. Count="$networkFailedChecks""

                                fi

                        else

                                if [[ "$networkFailedChecks" != 0 ]]

                                        then

                                                logger -t "$logTAG" "Network is working again"

                                fi

                                networkFailedChecks=0

                fi

		sleep "$checkInterval"

	done

