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

Začneme výpisem připojených usb zařízení:

```bash
lsusb
```

zkontrolujeme zda vidíme připojený SMS modem Huawei E3372h

následně potřebujeme zjistit k jakému souboru v /dev je mountován

```bash
dmesg | grep ttyUSB
```

abychom se k modemu pro jeho otestování připojili nainstalujeme následující nástroj

```bash
 apt install picocom -y
```

následně vyzkoušíme sériovou komunikaci

- v případě že by nebyl vidět vstup zapneme local echo CTRL+A, CTRL+C

```bash
picocom /dev/ttyUSB0 -b 19200 -l
AT 
#Modem odpoví OK pokud je v pořádku

AT+CSCS?    #Modem by měl odpovědět +CSCS: "GSM", pokud ne je potřeba zadat následující příkaz
    >AT+CSCS="GSM"  #Modem se přepne do GSM režimu

AT+CMGF?    #Modem by měl odpovědět +CMGF=1, to znamená že je aktivovana SMS komunikace, pokud ne je nutné tuto komunikace aktivovat
    >AT+CMGF=1  #Modem se přepne na SMS komunikace

AT+CMGS="+420605046201"      #Testovací SMS na číslo
> Toto je testovácí sms.  #Přidáme zprávu a potvrdíme CTRL+Z
```

ukončení picocom CTRL+A, CTRL+X

jako nástroj pro odesílání SMS zpráv použijme SMStools

```bash
 apt-get install smstools -y
 /etc/init.d/smstools start #zapneme službu
```

...pokračování v konfiguraci SMStools file

```bash
nano /etc/smsd.conf
```

```nano
incoming = /var/spool/sms/incoming
outgoing = /var/spool/sms/outgoing
sent = /var/spool/sms/sent
checked = /var/spool/sms/checked
failed = /var/spool/sms/failed

logfile = /var/log/smstools/smsd.log
stats = /var/log/smstools/smsd_stats

#pravděpodobně bude stačit editovat pouze GSM1 sekci
[GSM1]
#init =
device = /dev/ttyUSB0 #zde napsat cestu k zařízení
incoming = yes
baudrate = 19200
#pin = #zde uložte pin

```

restartujeme službu a mrkneme do logů zda vše proběhlo v pořádku

```bash
 /etc/init.d/smstools restart
 tail /var/log/smstools/smsd.log
```

přidáme script odesílání zpráv pro fungování **smstools** do PATH díky tomu se nám vytvoří nový bash příkaz *sendsms*

```bash
ls /usr/share/doc/smstools/examples/scripts/

mkdir /usr/smstools

 cp /usr/share/doc/smstools/examples/scripts/sendsms /usr/smstools

nano /usr/smstools/sendsms
    #ve sriptu nutné nastavit práva nově vytvořené sms
    chmod 0666 $TMPFILE

#a nastavit přístupová práva pro spuštění scriptu
 chmod -R 755 /usr/smstools

#cestu musíme ještě permanentně přidat do PATH to uděláme .profile nebo .bashrc
nano .profile
    PATH=$PATH:/usr/smstools
```

## Posílání zpráv

posílání zpráv teď funguje 2 způsoby

```bash
#1.
sendsms 420xxxxxxxxx 'Testovácí zpráva z SMStools'
```

vytvořením zprávy v ~var/smstools/sms/outgoing

```bash
#2.
cd /var/smstools/sms/outgoing

 nano
    To: 420xxxxxxxxx

    Toto je druha testovaci sms.
```

## API

stáhneme důležité balíky pro API

```bash
apt-get install apache mariadb-server php php-cli php-mysql php-gd php-curl php-mbstring php-xml php-zip -y
```

vytvoříme uživatele pro API playSMS

```bash
adduser playsms
usermod -a -G  playsms
```

nakonfigurujeme Apache VirtualHost

```bash
nano /etc/apache2/sites-available/playsms.conf
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

vytvoříme kořenový adresář pro playSMS

```bash
mkdir -p /home/playsms/{public_html,log,bin,etc,lib,src}
chmod -R 775 /home/playsms
chown playsms:playsms -R /home/playsms

touch /home/playsms/log/audit.log /home/playsms/log/playsms.log
chmod 664 /home/playsms/log/*
chown www-data.playsms -R /home/playsms/log
```

povolíme Apache, zapneme a načteme

```bash
a2ensite playsms.conf

#kontrola zda je syntaxe Apache service v pořádku
apachectl -t
systemctl start apache2.service
systemctl restart apache2.service
systemctl enable apache2.service
```

pokračujeme v nastavení MySQL

```bash
systemctl start mariadb.service
systemctl enable mariadb.service

mysql_secure_installation

Switch to unix_socket authentication [Y/n] n
Enter current password for root (enter for none): <Enter>
Set root password? [Y/n] y
Remove anonymous users? [Y/n] y
Disallow root login remotely? [Y/n] y
Remove test database and access to it? [Y/n] y
Reload privilege tables now? [Y/n] y
```

vytvoříme databázi

```bash
mysql -u root -p
CREATE DATABASE playsms;
CREATE USER 'playsms'@'localhost' IDENTIFIED BY 'playsms@123';
GRANT ALL PRIVILEGES ON playsms.* TO 'playsms'@'localhost';
FLUSH PRIVILEGES;
exit
```

```bash
su - playsms
cd /home/playsms/src
git clone -b 1.4.3 --depth=1 https://github.com/antonraharja/playSMS
cd playSMS¨

# INSTALL DATA
# ============
# Please change INSTALL DATA below to suit your system configurations
# Please do not change variable name, you may change only the value

# MySQL database username
DBUSER="playsms"

# MySQL database password
DBPASS="playsms@123"

# MySQL database name
DBNAME="playsms"

# MySQL database host
DBHOST="localhost"

# MySQL database port
DBPORT="3306"

# Web server's user, for example apache2 user by default is www-data
# note: please make sure your web server user
WEBSERVERUSER="www-data"

# Web server's group, for example apache2 group by default is www-data
# note: please make sure your web server group
WEBSERVERGROUP="www-data"

# Path to playSMS extracted source files
PATHSRC="/home/playsms/src/playSMS"

# Path to playSMS web files
# note: please make sure your web root path, in this example its /var/www/html
PATHWEB="/home/playsms/public_html"

# Path to playSMS additional files
PATHLIB="/home/playsms/lib"

# Path to playSMS daemon and other binary files
PATHBIN="/home/playsms/bin"

# Path to playSMS log files
PATHLOG="/home/playsms/log"

# Path to playSMS daemon configuration file
# note: this example will create playsmsd.conf in /etc
PATHCONF="/home/playsms/etc"

# END OF INSTALL DATA
# ===================

./install.sh
```

tím je API hotové

```bash

```

## Zdroje

https://sysopstechnix.com/build-your-own-sms-gateway-using-raspberry-pi/

https://gist.github.com/kmpm/10817304

https://www.developershome.com/sms/

https://pitigala.org/2011/12/30/how-to-setup-smstools-in-debian/