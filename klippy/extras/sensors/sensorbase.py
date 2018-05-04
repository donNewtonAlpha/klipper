# Printer heater support
#
# Copyright (C) 2018  Petri Honkala <cruwaller@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

SAMPLE_TIME_DEFAULT    = 0.001
SAMPLE_COUNT_DEFAULT   = 8
REPORT_TIME_DEFAULT    = 0.300

class error(Exception):
    pass

class SensorBase(object):
    error = error
    def __init__(self,
                 config,
                 is_spi = False,
                 sample_time  = SAMPLE_TIME_DEFAULT,
                 sample_count = SAMPLE_COUNT_DEFAULT,
                 report_time  = REPORT_TIME_DEFAULT):
        self.printer = config.get_printer()
        self.spi = is_spi # remove?
        self.sample_time = sample_time
        self.sample_count = sample_count
        self.min_temp = config.getfloat('min_temp', minval=0., default=0.)
        self.max_temp = config.getfloat('max_temp', above=self.min_temp)
        sensor_pin = config.get('sensor_pin')
        adc_range = [self.calc_adc(self.min_temp),
                     self.calc_adc(self.max_temp)]

        self.report_time = report_time

        ppins = self.printer.lookup_object('pins')
        if is_spi:
            self.mcu = ppins.setup_pin('thermocouple', sensor_pin)
            self.mcu.setup_spi_settings(
                config.getint('spi_mode', minval=0, maxval=3),
                config.getint('spi_speed', minval=0))
            self.mcu.setup_minmax(minval=min(adc_range),
                                  maxval=max(adc_range))
            self.mcu.setup_read_command(
                self.get_read_cmd(), self.get_read_bytes(),
                self.get_configs(), self.get_fault_filter())

        else:
            self.mcu = ppins.setup_pin('adc', sensor_pin)
            self.mcu.setup_minmax(
                sample_time, sample_count,
                minval=min(adc_range), maxval=max(adc_range))
    def get_mcu(self):
        return self.mcu.get_mcu()
    def get_min_max_temp(self):
        return self.min_temp, self.max_temp
    def setup_callback(self, cb):
        self.mcu.setup_callback(self.report_time, cb)
    def get_report_delta(self):
        # MCU reporting period already contains samples
        return self.report_time
        #return self.report_time + (self.sample_time *
        #                           self.sample_count)