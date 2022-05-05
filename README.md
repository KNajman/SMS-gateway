# SMS-gateway

SMS brána na Raspberry Pi

## Zadání

Zadáním je:

- na RaspberryPi vytvořit SMS bránu
- navrhnout bezpečné API pro vzdálené využití brány
- připravit demonstrační skripty pro vzdálené využití

## Implementace

### Raspberry setup

Přes ***Raspberry Pi Imager*** nahrajeme na SD kartu 32-bit nejnovější verzi *Raspberi OS - Debian*

Připojíme SMS modem, a zapneme zařízení

Přes protokol **SSH** a program ***PuTTy*** se následně k zařízení přípojíme jako:
pi@/'IPadresa zařízení/

### Konfigurace

Začneme konrolou připojených usb zařízení:

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

```bash
picocom /dev/ttyUSB0 -b 115200 -l
AT          #modem by měl odpovědět OK pokud je v pořáku
AT+CMGF=1   # odpověď OK pokud je podporováná SMS komunikace

AT+CMGS="+420xxxxxxxxx"      #Testovací SMS na číslo
> Toto je testovácí zpráva.  #Přidáme zprávu a CTRL+Z
+CMGS: 65
```

jako nástroj pro odesílání SMS zpráv použijme SMStools

```bash
sudo apt install smstools -y
```

...pokračování v konfiguraci SMStools file

- zatím nefuguje

posílání zpráv funguje 2 způsoby


```bash
# 1.
sendsms xxxxxxxxx 'Testovácí zpráva z SMStools'
```

vytvořením zprávy v ~var/smstools/sms/outgoing

```bash
# 2.
vim /var/smstools/sms/outgoing
To: 94771234505

Hello, this is the sms.

```

### API

pro API zvolíme PlaySMS
...pokud se nedojedná jinak
