"""
raspberry pi pin diagram: http://sustainablenetworks.org/CIS508/wp-content/uploads/2014/04/raspberry-pi-rev2-gpio-pinout.png
MOSI    P1-19
MISO    P1-21
SCLK    P1-23   P1-24    CE0
GND     P1-25   P1-26    CE1
"""

"""
Pin Assignments
"""

ADE_INT  = 2   #  Interrupt from ADE TODO
ADE_RST  = 3   #  ~Reset to ADE      TODO
ADE_CS   = 26  #  SPI ~chip select to ADE
ADE_CLK  = 23  #  SPI clock to ADE
ADE_MISO = 21  #  SPI MISO from ADE
ADE_MOSI = 19  #  SPI MOSI from ADE


"""
reverse  LSB/MSB
"""
def ReverseBits(byte):
    byte = ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)
    byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
    byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
    return byte

"""
print out a byte array in a human readable format (hexadecimal)
"""
def BytesToHex(Bytes):
     return ''.join(["0x%02X " % x for x in Bytes]).strip()
