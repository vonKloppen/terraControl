#!/bin/env python3

from oled import OLED, Font, Graphics
import syslog, signal, socket, os


socketType = "unix"
socketFile = "/run/terraDisplay.socket"
#socketType = "tcp"
#socketIP = "127.0.0.1"
#socketPort = "8888"

disp = OLED(1)
disp.begin()
disp.initialize()

disp.set_memory_addressing_mode(0)
disp.set_column_address(0, 127)
disp.set_page_address(0, 7)

disp.deactivate_scroll()

contrastDay = 127
contrastNight = 10


## SIGNAL HANDLING ###

def terminate(signalNumber, frame):

    logMessage("LOG_INFO", "SIGTERM received. Shutting down..")
    updateDisplay("X",1,0,0)
    syslog.closelog()
    exit(0)
    


if __name__ == '__main__':

    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, terminate)
    signal.signal(signal.SIGILL, signal.SIG_IGN)
    signal.signal(signal.SIGTRAP, signal.SIG_IGN)
    signal.signal(signal.SIGABRT, signal.SIG_IGN)
    signal.signal(signal.SIGBUS, signal.SIG_IGN)
    signal.signal(signal.SIGFPE, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGSEGV, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, terminate)

###


def logMessage(logLevel,message):

    syslog.syslog(getattr(syslog, logLevel), message)


def updateDisplay(status,terraNum,temp,hum):

    dispFont = Font(3)
    disp.clear()

    if status == "X":

        disp.set_contrast_control(contrastDay)
        dispFont.print_string(0, 0, "T: NONE")
        dispFont.print_string(0, 27, "H: NONE")
        terraNum = status

    else:

        dispFont.print_string(0, 0, "T: " + temp)
        dispFont.print_string(0, 27, "H: " + hum)

    dispFont = Font(1)
    dispFont.print_string(0, 57, "Terra: " + str(terraNum) + "    " + "Status: " + status)
    disp.update()


def runServer():

    if socketType == "unix":

        if os.path.exists(socketFile):

            try:
                os.remove(socketFile)

            except:
                logMessage("LOG_ERR", "Failed to delete socket file")
                exit(1)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            server.bind(socketFile)

        except: 
            logMessage("LOG_ERR", "Failed to bind to socket..")
            exit(1)


        server.listen(0)
        client_socket, client_address = server.accept()

        while True:

            try:
                request = client_socket.recv(1024)
                request = request.decode("utf-8")

                if len(request) == 0:

                    client_socket.close()
                    continue

            except:
                client_socket.close()
                server.listen(0)
                client_socket, client_address = server.accept()
                continue

            request = request.split(',')

            try:
                updateDisplay(request[0],request[1],request[2],request[3])

            except:
                client_socket.close()
                logMessage("LOG_ERR", "Failed to update screen..")

        client_socket.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        syslog.closelog()
        exit(0)

runServer()

