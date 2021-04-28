"""
about GSPHeader:

* struct:

    - seq: sequance number
    - type: 0 for control, 1 for data
    - fn: only for control
        + three way handshake:
            + 0: request for connection
            + 1: same of "SYN,ACK", means got request
            + 2: ACK for "ACK"
        + normal control:
            + 3: stop transmission
        + congestion control:
            + 4: can't catch up, lower the quality
            + 5: normal transmission for 10 frame, increase quality
        + screen resolution check:
            + 6: send resolution
            + 7: ACK for resolution check
    - frm: frame number
    - last: whether this is the last packet for the frame
    - timestamp: as it is

about GSSPBody:
    - type:
        + 0: mouse
        + 1: keyboard
    - action:
        + general:
            + 0: press
            + 1: release
        + for mouse:
            + 2: move
            + 3: scroll
    - x,y: for mouse
    - btn: for keyboard
    - special:
        + 0: no use
        + 1: up
        + 2: down
        + 3: left
        + 4: right
        + 5: enter
        + 6: esc
"""
from ctypes import *


class GSP:
    CONTROL = 0
    DATA = 1
    RQST_CONN = 0
    SYN_ACK = 1
    ACK = 2
    STOP = 3
    CONGESTION = 4
    RES = 6
    RES_ACK = 7
    NONE = 0


class GSPHeader(Structure):
    _fields_ = [
        ('seq', c_uint),
        ('type', c_uint8),
        ('fn', c_uint8),
        ('frm', c_uint8),
        ('last', c_uint8),
        ('timestamp', c_double)
    ]


class GSSP:
    MOUSE = 0
    KEYBOARD = 1
    P = 0
    R = 1
    M = 2
    S = 3
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    ENTER = 5
    ESC = 6
    NO_BTN = b'\0'


class GSSPBody(Structure):
    _fields_ = [
        ('type', c_uint8),
        ('action', c_uint8),
        ('x', c_uint16),
        ('y', c_uint16),
        ('btn', c_char),
        ('special', c_uint8)
    ]
