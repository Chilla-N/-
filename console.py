from concurrent.futures import process
from time import sleep
import os
import subprocess

os.system("Get-VM | where {$_.State -eq 'Running'}")
sleep(1)
os.system('VMName = "VMNAME"')
sleep(0.1)
os.system("VM = @{\Name = $VMName")
sleep(0.1)
os.system("MemoryStartupBytes = 2147483648")
sleep(0.1)

os.system("Generation = 2")
sleep(0.1)

os.system('NewVHDPath = "C:\Virtual Machines\$VMName\$VMName.vhdx"')
sleep(0.1)

os.system("NewVHDSizeBytes = 53687091200")
sleep(0.1)

os.system('BootDevice = "VHD"')
sleep(0.1)

os.system('Path = "C:\Virtual Machines\$VMName"')

sleep(0.1)

os.system("SwitchName = (Get-VMSwitch).Name")
