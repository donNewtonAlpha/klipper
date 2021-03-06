# AD5206 digipot code
#
# Copyright (C) 2017,2018  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

class ad5206:
    def __init__(self, config):
        ppins = config.get_printer().lookup_object('pins')
        enable_pin = config.get('enable_pin')
        enable_pin_params = ppins.lookup_pin('digital_out', enable_pin)
        if enable_pin_params['invert']:
            raise ppins.error("ad5206 can not invert pin")
        mcu = enable_pin_params['chip']
        pin = enable_pin_params['pin']
        scale = config.getfloat('scale', 1., above=0.)
        channels = [None]*6
        for i in range(len(channels)):
            val = config.getfloat('channel_%d' % (i+1,), None,
                                  minval=0., maxval=scale)
            if val is not None:
                channels[i] = int(val * 256. / scale + .5)
        oid = mcu.create_oid()
        mcu.add_config_cmd(
            "config_spi oid=%d bus=%d pin=%s inverted=%u mode=%u rate=%u shutdown_msg=" % (
                oid, 0, pin, False, 0, 25000000))
        for i, val in enumerate(channels):
            if val is not None:
                mcu.add_config_cmd(
                    "spi_send oid=%d data=%02x%02x" % (oid, i, val),
                    is_init=True)

def load_config_prefix(config):
    return ad5206(config)
