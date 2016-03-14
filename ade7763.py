import wiringpi2 as wiringpi
# import RPi.GPIO as GPIO
import spidev
import time
# from pins import *

# Set up SPI
spi = spidev.SpiDev()
spi.open(0, 1)                      # spi.open(bus, device)
spi.max_speed_hz = 7629             # TODO what speed should this be?

# Set up GPIO pins
wiringpi.wiringPiSetup()

# configure chip select
# TODO do I need to do this or
# does xfer take care of it?
wiringpi.pinMode(ADE_CS, OUTPUT)
wiringpi.digitalWrite(ADE_CS, HIGH)
time.sleep(0.01)

# configure reset
wiringpi.pinMode(ADE_RST, OUTPUT)
wiringpi.digitalWrite(ADE_RST, HIGH)

try:
    while True:
        opt = input("> ")

        if opt == "r" or opt == "reset_ade":
            print "Resetting ADE\n"
            ade_reset()
        elif opt == "R" or opt == "reset":
            print "Resetting peak values\n"
            ade_reset_peaks()
        elif opt == "i":
            print "Read Current Channel 1 RMS reg value\n"
            r = ade_read(MR_IRMS, MR_IRMS_CNT)
            print "IRMS 0x" + BytesToHex(r) + "\n"
        elif opt == "v":
            print "Read Voltage Channel 2 RMS reg value\n"
            r = ade_read(MR_VRMS, MR_VRMS_CNT)
            print "VRMS 0x" + BytesToHex(r) + "\n"
        elif opt == "I":
            print "Read Current Channel Peak reg value\n"
            r = ade_read(MR_IPEAK, MR_IPEAK_CNT)
            print "IPEAK 0x" + BytesToHex(r) + "\n"
        elif opt == "V":
            print "Read Voltage Channel Peak reg value\n"
            r = ade_read(MR_VPEAK, MR_VPEAK_CNT)
            print "VPEAK 0x" + BytesToHex(r) + "\n"
        elif opt == "h" or opt == "help":
            s = ("r\t\t\treset ADE\n"
                    "R\t\t\tReset peak values\n"
                    "i\t\t\tPrint current channel 1 RMS reg value\n"
                    "v\t\t\tPrint voltage channel 2 RMS reg value\n"
                    "I\t\t\tPrint current peak reg value\n"
                    "V\t\t\tPrint voltage peak reg value\n"
                    )
            print s
        else:
            print "Unknown command\n"
except KeyboardInterrupt: # Ctrl+C pressed, so…
    spi.close()




def ade_reset():
    wiringpi.digitalWrite(ADE_RST, OFF)
    time.sleep(0.100)
    wiringpi.digitalWrite(ADE_RST, ON)
    time.sleep(0.100)


def ade_reset_peaks():
    ade_read(MR_RAENERGY, MR_RAENERGY_CNT)
    print "Reset AENERGY"

    ade_read(MR_RVAENERGY, MR_RVAENERGY_CNT)
    print "Reset VAENERGY"

    ade_read(MR_RSTIRQ,    MR_RSTIRQ_CNT)
    print "Reset IRQ"

    ade_read(MR_RSTIPEAK,  MR_RSTIPEAK_CNT)
    print "Reset IPEAK"

    ade_read(MR_RSTVPEAK,  MR_RSTVPEAK_CNT)
    print "Reset VPEAK"


def ade_read(addr, count):
    # select the chip
    wiringpi.digitalWrite(ADE_CS, LOW)
    time.sleep(0.01)

    # write address to access
    spi.xfer2([addr])
    time.sleep(0.004)

    # read
    r = spi.readbytes(count)

    # TODO might need to flip around bits here,
    # need to

    # deselect the chip
    wiringpi.digitalWrite(ADE_CS, HIGH)
    time.sleep(0.100)

    return r

