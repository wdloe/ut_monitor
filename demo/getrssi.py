# GET RSSI DATA

import serial
import time
import requests

# autoconnect
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
ut_port = p[0] #working perfectly on my Huawei Modem

#ut_port='/dev/ttyUSB0' #by default, in first after boot will be USB0
ut=serial.Serial(ut_port, 115200, timeout=2)
print()
print(ut.name)

#check OK
cmd_ok='AT\r'
ut.write(cmd_ok.encode())
print('Getting device ready ... ')

ut_ok=ut.readline() #blank
ut_ok=ut.readline() #OK
ut_ok=ut_ok.decode('utf-8')
oke=ut_ok[0:2]
if oke=='OK':
    print(oke+': Your device is ready')
else:
    print(oke+': Your device is not ready. Please try again')
    
#checking device IMEI
ut.reset_output_buffer()
cmd_imei='AT+CGSN\r'
ut.write(cmd_imei.encode())
print()
print('Getting device information ... ')

ut_cgsn=ut.readline() #blank
ut_cgsn=ut.readline() #IMEI
ut_cgsn=ut_cgsn.decode('utf-8')
imei=ut_cgsn[0:15] #unique id upload to server
imei=int(imei) #convert to integer as spec
print("IMEI : " + str(imei))

while True:
	#getting RSSI data
	ut.reset_output_buffer()
	cmd_csq='AT+CSQ\r'
	epoch=int(time.time())
	ut.write(cmd_csq.encode())
	print()
	print('Getting RSSI ... ')

	ut_csq=ut.readline() #blank
	ut_csq=ut.readline() #OK
	ut_csq=ut.readline() #blank
	ut_csq=ut.readline() #CSQ
	ut_csq=ut_csq.decode('utf-8')
		
	colon=ut_csq.find(',')
	rssi=ut_csq[colon-2:colon]
	ber=ut_csq[colon+1:colon+3]
	rssi=int(rssi)
	ber=int(ber)
	csq=float(rssi-95) #meraki formula dbm https://documentation.meraki.com/MR/Monitoring_and_Reporting/Location_Analytics
	print("Timestamp: " + str(epoch))
	print("Signal strength: " + str(csq) + " dBm")
	print("RSSI: " + str(rssi))
	print("BER: " + str(ber))
		
	json={"csq":csq,"id":imei,"ts": epoch}
	response = requests.post("https://vms.inmarsat.com/apiv2", json=json)
	print(json)
	print("Status code: ", response.status_code)
	time.sleep(5)
    
