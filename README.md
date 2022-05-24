# SMS-gateway

SMS brána na Raspberry Pi

## Zadání

Zadáním je:

- na RaspberryPi vytvořit SMS bránu
- navrhnout bezpečné API pro vzdálené využití brány
- připravit demonstrační skripty pro vzdálené využití

## Specifikace zařízeni pro implementaci

### SIM info

telefoní číslo : 704 953 258
PIN(zrušen) :1400

### Modem info

Huawei E3372h

## Implementace

### Raspberry setup

Přes ***Raspberry Pi Imager*** nahrajeme na SD kartu 32-bit nejnovější verzi *Raspberi OS - Debian*

Připojíme SMS modem, a zapneme zařízení

Přes protokol **SSH** a program ***PuTTy*** se následně k zařízení přípojíme jako:
pi@/'IPadresa zařízení/

### Konfigurace

Začneme konTrolou připojených usb zařízení:

```bash
lsusb
```

zkontrolujeme zda vidíme připojený SMS modem

následně potřebujeme zjistit k jakému souboru je mountován

```bash
dmesg | grep ttyUSB
```

abychom se k modemu pro jeho otestování připojili nainstalujeme následující nástroj

```bash
sudo app install picocom -y
```

následně vyzkoušíme sériovou komunikaci

- v případě že by nebyl vidět vstup zapneme local echo CTRL+A, CTRL+C

```bash
picocom /dev/ttyUSB0 -b 115200 -l
AT 
#Modem odpoví OK pokud je v pořádku

AT+CSCS?    #Modem by měl odpovědět +CSCS: "GSM", pokud ne je potřeba zadat následující příkaz
    >AT+CSCS="GSM"  #Modem se přepne do GSM režimu

AT+CMGF?    #Modem by měl odpovědět +CMGF=1, to znamená že je aktivovana SMS komunikace, pokud ne je nutné tuto komunikace aktivovat
    >AT+CMGF=1  #Modem se přepne na SMS komunikace

AT+CMGS="+420xxxxxxxxx"      #Testovací SMS na číslo
> Toto je testovácí sms.  #Přidáme zprávu a potvrdíme CTRL+Z
+CMGS: 65
```

ukončení picocom CTRL+A, CTRL+X

jako nástroj pro odesílání SMS zpráv použijme SMStools

```bash
sudo apt-get install smstools -y
sudo /etc/init.d/smstools start #zapneme službu
```

...pokračování v konfiguraci SMStools file

```bash
sudo nano /etc/smsd.conf
#stačí editovat pouze GSM1 sekci
[GSM1]
#init =
device = /dev/ttyUSB1 #zde napsat cestu k zařízení
incoming = yes
pin = 1400 #zde uložte pin
baudrate = 115200
```

zapneme službu a mrkneme do logů zda vše proběhlo v pořádku

```bash
sudo /etc/init.d/smstools restart
sudo tail /var/log/smstools/smsd.log
```

## posílání zpráv

posílání zpráv funguje 2 způsoby

```bash
#1.
sendsms xxxxxxxxx 'Testovácí zpráva z SMStools'
```

vytvořením zprávy v ~var/smstools/sms/outgoing

```bash
#2.
sudo nano /var/smstools/sms/outgoing/
To: 420xxxxxxxxx

Toto je druha testovaci sms.
```

### API

```bash
sudo nano 
<VirtualHost *:80>
    ServerName smsgw.sysopstechnix.com
    DocumentRoot /home/playsms/public_html
    ErrorLog /home/playsms/log/httpd-error.log
    CustomLog /home/playsms/log/httpd-accesss.log combined
    <Directory /home/playsms/public_html>
        AllowOverride FileInfo AuthConfig Limit Indexes
        Options MultiViews Indexes SymLinksIfOwnerMatch IncludesNoExec
        Require method GET POST OPTIONS
        php_admin_value engine On
    </Directory>
</VirtualHost>
```


pro API zvolíme PlaySMS
...pokud se nedojedná jinak

### Zdroje

https://sysopstechnix.com/build-your-own-sms-gateway-using-raspberry-pi/

https://gist.github.com/kmpm/10817304

https://www.developershome.com/sms/

https://pitigala.org/2011/12/30/how-to-setup-smstools-in-debian/