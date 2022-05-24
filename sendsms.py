import os
import gammu

gammu.SetDebugFile('/tmp/gammu.log')

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Send SMS')
    parser.add_argument('-m', '--message', help='Message to send', required=True)
    parser.add_argument('-n', '--number', help='Number to send to', required=True)
    return parser.parse_args()



if __name__ == "__main__":
    sms = gammu.SMS()
    sms.SetSMSC(gammu.SMSC(Location=1))
    sms.SetReceiving(True)
    sms.SetSMS(gammu.EncodeSMS(
        SMSC=None,
        Number=+420605046201,
        Text='Hello world!'))
    sms.Send()
    
    