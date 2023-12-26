#!/usr/bin/python3
"""OmnikExport program.

Get data from an omniksol inverter with 602xxxxx - 606xxxx ans save the data in
a database or push to pvoutput.org.
"""
import socket  # Needed for talking to inverter
import sys
import logging
import logging.config
import configparser
import os
import time
from InverterMsg import InverterMsg  # Import the Msg handler


class OmnikExport:
    """
    Get data from Omniksol inverter and store the data in a configured output
    format/location.
    """

    config = None
    logger = None

    def __init__(self, config_file):
        # Load the setting
        config_files = [self.__expand_path('config-default.cfg'),
                        self.__expand_path(config_file)]

        self.config = configparser.RawConfigParser()
        self.config.read(config_files)

    def run(self):
        """Get information from inverter and store is configured outputs."""
        self.build_logger(self.config)

        # Connect to inverter
        ip = self.config.get('inverter', 'ip')
        port = self.config.get('inverter', 'port')

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

        wifi_serial = self.config.getint('inverter', 'wifi_sn')
        inverter_socket.sendall(OmnikExport.generate_string(wifi_serial))
        data = inverter_socket.recv(1024)
        inverter_socket.close()

        msg = InverterMsg(data)

        return self.print_prometheus_logs(msg)

    def print_prometheus_logs(self, msg):
        timestamp = int(time.time())

        logs = ""

        logs += "e_today_kwh{device=\"%s\"} %.2f %d\n" % (
            msg.id, msg.e_today, timestamp)
        logs += "e_total_kwh{device=\"%s\"} %.2f %d\n" % (
            msg.id, msg.e_total, timestamp)
        logs += "h_total_degrees{device=\"%s\"} %.2f %d\n" % (
            msg.id, msg.h_total / 1000, timestamp)

        for i in range(1, 4):
            logs += "pv_voltage_volts{device=\"%s\", pv=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.v_pv(i), timestamp)
            logs += "pv_current_amps{device=\"%s\", pv=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.i_pv(i), timestamp)

        for i in range(1, 4):
            logs += "ac_voltage_volts{device=\"%s\", line=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.v_ac(i), timestamp)
            logs += "ac_current_amps{device=\"%s\", line=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.i_ac(i), timestamp)
            logs += "ac_power_watts{device=\"%s\", line=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.p_ac(i), timestamp)
            logs += "ac_frequency_hertz{device=\"%s\", line=\"%d\"} %.2f %d\n" % (
                msg.id, i, msg.f_ac(i), timestamp)

        return logs

    def build_logger(self, config):
        # Build logger
        """
        Build logger for this program

        Args:
            config: configparser with settings from file
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
        self.config.set(section, option, value)

    @staticmethod
    def __expand_path(path):
        """
        Expand relative path to absolute path.

        Args:
            path: file path

        Returns: absolute path to file

        """
        if os.path.isabs(path):
            return path
        else:
            return os.path.dirname(os.path.abspath(__file__)) + "/" + path

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
        hex_list = [format(int(double_hex[i:i + 2], 16), '02x').encode('ascii') for i in
                    reversed(range(0, len(double_hex), 2))]
        
        cs_count = 115 + sum([int(c, 16) for c in hex_list])
        checksum = format(cs_count, '02x').encode('ascii')
        response += b''.join(hex_list) + b'\x01\x00' + checksum + b'\x16'
        return response



