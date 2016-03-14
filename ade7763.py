import RPi.GPIO as GPIO
import spidev
import time
from pins import *

# Set up SPI
spi = spidev.SpiDev()
spi.open(0, 1)                      # spi.open(bus, device)
spi.max_speed_hz = 7629             # TODO what speed should this be?

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)

# TODO configure chip select - is this
# required or handled by spidev?

# configure reset
GPIO.setup(ADE_RST, GPIO.OUT)
GPIO.output(ADE_RST, GPIO.HIGH)

# configure interrupt pin
# GPIO.setup(ADE_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(ADE_INT, GPIO.FALLING, callback=ade_isr, bouncetime=300)

ade_config()

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
    GPIO.cleanup()



def ade_reset():
    GPIO.output(ADE_RST, GPIO.LOW)
    time.sleep(0.100)
    GPIO.output(ADE_RST, GPIO.HIGH)
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


def ade_config():
    ui, uc = 0, 0

    # reset
    ade_reset()

    # perform software reset
    ui = ade_read(MR_MODE, ui, MR_MODE_CNT)
    ui |= MODE_SWRST
    ADE_write(MR_MODE, ui, MR_MODE_CNT)
    time.sleep(0.20); # Wait for reset to take effect

    # Get die version
    uc = ade_read (MR_DIEREV, MR_DIEREV_CNT)

    # Write to Mode register
    ui = 0x00 | \
        MODE_DISLPF2   |    \
        MODE_DISCF     |    \
        MODE_DISSAG    |    \
        MODE_WAV_POWER |    \
        0x00
        # MODE_DISLPF2   |    \ # Disable LPF after the multiplier (LPF2)
        # MODE_DISCF     |    \ # Disable frequency output
        # MODE_DISSAG    |    \ # Disable line voltage sag detection
        # MODE_WAV_POWER |    \ # Sample active power
        # MODE_DISHPF    |   // Disable HPF in Channel 1
        # MODE_ASUSPEND  |   // Disable A/D converters
        # MODE_TEMPSEL   |   // Start temperature conversion
        # MODE_SWRST     |   // Software Chip Reset.
        # MODE_CYCMODE   |   // Enable line cycle accumulation mode
        # MODE_DISCH1    |   // Short out Chan1 (Current)
        # MODE_DISCH2    |   // Short out Chan2 (Voltage)
        # MODE_SWAP      |   // Swap Chan1 and Chan2
        # MODE_DTRT_3K5  |   // Waverform data rate to 3.5ksps
        # MODE_POAM      |   // Accumulated positive power only


    # Set the mode
    ade_write(MR_MODE, ui, MR_MODE_CNT)

    # Write to interrupt enable register
    ui = IRQ_NONE;
    ade_write(MR_IRQEN, ui, MR_IRQEN_CNT)

    # Reset interrupt status (with reset)
    ui = ade_read(MR_RSTIRQ, MR_RSTIRQ_CNT)

    # Set up the gain register
    uc = 0x00  # ADC1,2 gain = 1 full scale range is +-0.5V
    ade_write(MR_GAIN, uc, MR_GAIN_CNT)

    # Set up the offset correction for ADC1
    uc = 0x00
    ade_write(MR_CH1OS, uc, MR_CH1OS_CNT)

    # Set up the offset correction for ADC2
    uc = 0x00
    ade_write (MR_CH2OS, uc, MR_CH2OS_CNT)

    return



def ade_read(addr, count):
    # TODO select the chip
    GPIO.output(ADE_CS, GPIO.LOW)
    time.sleep(0.01)

    # write address to access
    spi.xfer2([addr])
    time.sleep(0.004)

    # read
    r = spi.readbytes(count)

    # TODO might need to flip around bits here

    # TODO deselect the chip
    wiringpi.digitalWrite(ADE_CS, HIGH)
    time.sleep(0.100)

    return r


def ade_write(addr, data, count):
    # TODO select the chip
    GPIO.output(ADE_CS, GPIO.LOW)
    time.sleep(0.01)

    # write address to access
    spi.xfer2(addr | ADE_WRITE_FLAG)
    time.sleep(0.004)

    # read
    r = spi.writebytes(data)

    # TODO might need to flip around bits here

    # TODO deselect the chip
    wiringpi.digitalWrite(ADE_CS, HIGH)
    time.sleep(0.100)

    return r


def ade_isr(channel):
    irqstat, irqen = 0, 0

    # Read IRQ Status and reset
    irqstat = ade_read(MR_RSTIRQ, MR_RSTIRQ_CNT)

    #  Sample available
    if irqstat & IRQ_WSMP:
        # Read waveform register to get sample
        sample_ = ade_read(MR_WAVEFORM, MR_WAVEFORM_CNT)

        # Clear bit in interrupt enable register to stop sampling
        irqen = ade_read(MR_IRQEN, MR_IRQEN_CNT)
        irqen = irqen & ~IRQ_WSMP
        ade_write (MR_IRQEN, irqen, MR_IRQEN_CNT)



