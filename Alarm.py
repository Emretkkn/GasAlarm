from smtplib import SMTP
import RPi.GPIO as GPIO
import time

SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
mq2_dpin = 26
mq2_apin = 0
led1 = 17
led2 = 26
led3 = 6
buzzer = 5
subcjet = "UYARI"
message = "Yüksek gaz sızıntısı !"
content = "Subject: {0}\n\n{1}".format(subcjet,message)
myMailAdress = "emretkn3510@gmail.com"
password = "******"
sendTo = "emretkn1035@gmail.com"
mail = SMTP("smtp.gmail.com", 587)
mail.ehlo()
mail.starttls()
mail.login(myMailAdress,password)

def init():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
    GPIO.setup(mq2_dpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(led1, GPIO.OUT)
    GPIO.setup(led2, GPIO.OUT)
    GPIO.setup(led3, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)





# read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
def readadc(
    adcnum,
    clockpin,
    mosipin,
    misopin,
    cspin,
    ):
    if adcnum > 7 or adcnum < 0:
        return -0x1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if commandout & 0x80:
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 0x1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 0x1
        if GPIO.input(misopin):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 0x1  # first bit is 'null' so drop it
    return adcout

def main():
    init()
    print ('lutfen bekleyiniz...')
    time.sleep(10)
    while True:
        COlevel = readadc(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        dumandeger = COlevel / 1024. * 3.3

        if dumandeger > 1:
                GPIO.output(led1,True)
        else:
                GPIO.output(led1,False)

        if dumandeger > 0.7:
                GPIO.output(5,1)
        else:
                GPIO.output(5,0)

        if dumandeger > 0.7 and dumandeger < 1.2:
                GPIO.output(led2,True)
        else:
                GPIO.output(led2,False)

        if dumandeger < 0.7:
                GPIO.output(led3,True)
        else:
                GPIO.output(led3,False)

        if dumandeger > 1 and dumandeger < 2:
                mail.sendmail(myMailAdress, sendTo, content.encode("utf-8"))





        time.sleep(0.5)
        print ('Olculen AD degeri: ' + str('%.2f' % dumandeger) + ' V')





if __name__ == '__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        pass

GPIO.cleanup()