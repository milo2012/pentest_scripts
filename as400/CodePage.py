"""
CodePage
Used to convert ascii to ebcdic and ebcdic to ascii
Created by Kenneth J. Pouncey 2002-05-18
Changed by Nate Custer - 2002-05-22
    Used some different data types to improve performance/memory usage.
    Used a dict (hash table) instead of a list for the lookup tables.
    The performance of a lookup is faster if you use a dict. Also; used a
    tuple instead of a list for the list at the start. Since tuples aren't
    mutable the python interpreter uses less memory to store them.
Cleaned up by P. Bielen - 2002-05-23
    Managed a length of 75 characters at one line, to prevend a lot of
    editors to do a word-wrap.
"""

__all__ = ["CodePage"]

# Tunable parameters
DEBUGLEVEL = 0

# Conversion table generated mechanically by Free `recode' 3.5
# for sequence IBM037..ISO-8859-1 (reversible).  */

codePage37 = ( 0,   1,   2,   3, 156,   9, 134, 127, 151, 141, 142,  11, \
               12,  13,  14,  15, 16,  17,  18,  19, 157, 133,   8, 135, \
               24,  25, 146, 143, 28,  29,  30,  31, 128, 129, 130, 131, \
               132,  10,  23,  27, 136, 137, 138, 139, 140,   5,   6, \
               7, 144, 145,  22, 147, 148, 149, 150,   4, 152, 153, 154, \
               155,  20,  21, 158,  26, 32, 160, 226, 228, 224, 225, 227, \
               229, 231, 241, 162,  46,  60,  40,  43, 124, 38, 233, 234, \
               235, 232, 237, 238, 239, 236, 223,  33,  36,  42,  41, \
               59, 172, 45,  47, 194, 196, 192, 193, 195, 197, 199, 209, \
               166,  44,  37,  95,  62,  63, 248, 201, 202, 203, 200, \
               205, 206, 207, 204,  96,  58,  35,  64,  39,  61,  34, \
               216,  97,  98,  99, 100, 101, 102, 103, 104, 105, 171, \
               187, 240, 253, 254, 177, 176, 106, 107, 108, 109, 110, \
               111, 112, 113, 114, 170, 186, 230, 184, 198, 164, 181, \
               126, 115, 116, 117, 118, 119, 120, 121, 122, 161, 191, \
               208, 221, 222, 174, 94, 163, 165, 183, 169, 167, 182, 188, \
               189, 190,  91,  93, 175, 168, 180, 215, 123,  65,  66, \
               67,  68,  69,  70,  71, 72,  73, 173, 244, 246, 242, 243, \
               245, 125,  74,  75,  76,  77,  78,  79,  80, 81,  82, 185, \
               251, 252, 249, 250, 255, 92, 247,  83,  84,  85,  86,  87, \
               88, 89,  90, 178, 212, 214, 210, 211, 213, 48,  49,  50, \
               51,  52,  53,  54,  55, 56,  57, 179, 219, 220, 217, 218, \
               159)

class CodePage:                             #CodePage class.
    def __init__(self,codePage=None):       #Constructor.
        if codePage:
            self.setCodePage(codePage)
        else:
            self.setCodePage(37)

    def setCodePage(self,codePage):
        self.ascii = {}
        self.ebcdic = {}
        if codePage == 37:
            cp = codePage37
        else:
            cp = codePage37
        cpi = 0
        while cpi < 256:
            self.ebcdic[cpi] = cp[cpi]
            self.ascii[cp[cpi]] = cpi
            cpi += 1

    def getEBCDIC (self,index):
        return self.ascii[index]

    def getEBCDICChar (self,index):
        return chr(self.ascii[index])

    def getASCII (self,index):
        return self.ebcdic[index]

    def getASCIIChar (self,index):
        return chr(self.ebcdic[index])

    def ebcdic2uni (self,index):
        return self.getASCIIChar(index)

    def uni2ebcdic (self,index):
        return self.getEBCDICChar(ord(index))