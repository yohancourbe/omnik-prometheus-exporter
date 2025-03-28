#!/usr/bin/python3
"""OmnikExport program.

Get data from an omniksol inverter with 602xxxxx - 606xxxx ans save the data in
a database or push to pvoutput.org.
"""
import socket  # Needed for talking to inverter
import sys
import logging
import logging.config
import os
import time
from InverterMsg import InverterMsg  # Import the Msg handler
import codecs
import re

class OmnikExport:
    """
    Get data from Omniksol inverter and store the data in a configured output
    format/location.
    """

    logger = None

    def __init__(self):
        pass

    def run(self):
        """Get information from inverter and store is configured outputs."""
        self.build_logger()

        # Connect to inverter
        ip = os.getenv('INVERTER_IP')
        port = os.getenv('INVERTER_PORT')

        for res in socket.getaddrinfo(ip, port, socket.AF_INET,
                                      socket.SOCK_STREAM):
            family, socktype, proto, canonname, sockaddress = res
            try:
                self.logger.info('connecting to {0} port {1}'.format(ip, port))
                inverter_socket = socket.socket(family, socktype, proto)
                inverter_socket.settimeout(10)
                inverter_socket.connect(sockaddress)
            except socket.error as msg:
                self.logger.error('Could not open socket')
                self.logger.error(msg)
                sys.exit(1)

        wifi_serial = int(os.getenv('INVERTER_WIFI_SN'))
        inverter_socket.sendall(OmnikExport.generate_string(wifi_serial))
        data = inverter_socket.recv(1024)
        inverter_socket.close()

        msg = InverterMsg(data)

        return self.print_prometheus_logs(msg)

    def print_prometheus_logs(self, msg):
        timestamp = int(time.time())

        logs = ""

        logs += "e_today_kwh{device=\"%s\"} %.2f\n" % (msg.id, msg.e_today)
        logs += "e_total_kwh{device=\"%s\"} %.2f\n" % (msg.id, msg.e_total)
        logs += "h_total_degrees{device=\"%s\"} %.2f\n" % (msg.id, msg.h_total / 1000)

        for i in range(1, 4):
            logs += "pv_voltage_volts{device=\"%s\", pv=\"%d\"} %.2f\n" % (msg.id, i, msg.v_pv(i))
            logs += "pv_current_amps{device=\"%s\", pv=\"%d\"} %.2f\n" % (msg.id, i, msg.i_pv(i))

        for i in range(1, 4):
            logs += "ac_voltage_volts{device=\"%s\", line=\"%d\"} %.2f\n" % (msg.id, i, msg.v_ac(i))
            logs += "ac_current_amps{device=\"%s\", line=\"%d\"} %.2f\n" % (msg.id, i, msg.i_ac(i))
            logs += "ac_power_watts{device=\"%s\", line=\"%d\"} %.2f\n" % (msg.id, i, msg.p_ac(i))
            logs += "ac_frequency_hertz{device=\"%s\", line=\"%d\"} %.2f\n" % (msg.id, i, msg.f_ac(i))

        return logs

    def build_logger(self):
        # Build logger
        """
        Build logger for this program
        """
        log_levels = dict(debug=10, info=20, warning=30, error=40, critical=50)
        log_dict = {
            'version': 1,
            'formatters': {
                'f': {'format': '%(asctime)s %(levelname)s %(message)s'}
            },
            'handlers': {
                'none': {'class': 'logging.NullHandler'},
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'f'
                }
            },
            'loggers': {
                'OmnikLogger': {
                    'handlers': ['console'],
                    'level': log_levels["info"]
                }
            }
        }
        logging.config.dictConfig(log_dict)
        self.logger = logging.getLogger('OmnikLogger')

    def override_config(self, section, option, value):
        """Override config settings"""
        os.environ[option] = value

    @staticmethod
    def generate_string(serial_no):
        """Create request string for inverter.
    
        The request string is built from several parts. The first part is a
        fixed 4 char string; the second part is the reversed hex notation of
        the s/n twice; then again a fixed string of two chars; a checksum of
        the double s/n with an offset; and finally a fixed ending char.
    
        Args:
            serial_no (int): Serial number of the inverter
    
        Returns:
            bytes: Information request string for inverter
        """
        response = b'\x68\x02\x40\x30'

        double_hex = hex(serial_no)[2:] * 2

        # changed for python3
        hex_list = [codecs.decode(double_hex[i:i + 2], 'hex') for i in
                    reversed(range(0, len(double_hex), 2))]

        cs_count = 115 + sum([ord(c) for c in hex_list])

        # changed for python3
        checksum = codecs.decode(hex(cs_count)[-2:], 'hex')

        # changed for python3
        response += b''.join(hex_list) + b'\x01\x00' + checksum + b'\x16'

        return response
