import json
import struct
import socket
socket.setdefaulttimeout(5.0)


class HS110:

    def __init__(self, ip, port=9999):
        self.ip = ip
        self.port = port
        self.sock = None

        # Available commands in cleartext
        self.COMMANDS = {
            'info'     : '{"system":{"get_sysinfo":{}}}',
            'on'       : '{"system":{"set_relay_state":{"state":1}}}',
            'off'      : '{"system":{"set_relay_state":{"state":0}}}',
            'led_on'   : '{"system":{"set_led_off":{"off":0}}}',
            'led_off'  : '{"system":{"set_led_off":{"off":1}}}',
            'state'    : '{"system":{"get_sysinfo":{}}}',
            'cloudinfo': '{"cnCloud":{"get_info":{}}}',
            'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
            'time'     : '{"time":{"get_time":{}}}',
            'schedule' : '{"schedule":{"get_rules":{}}}',
            'countdown': '{"count_down":{"get_rules":{}}}',
            'antitheft': '{"anti_theft":{"get_rules":{}}}',
            'reboot'   : '{"system":{"reboot":{"delay":1}}}',
            'reset'    : '{"system":{"reset":{"delay":1}}}',
            'energy'   : '{"emeter":{"get_realtime":{}}}'
        }

        # Encrypt commands for direct usage
        for cmd_name in self.COMMANDS.keys():
            self.COMMANDS[cmd_name] = self._encrypt(self.COMMANDS[cmd_name])

    def _encrypt(self, string):
        key = 0xAB
        plainbytes = string.encode()
        buffer = bytearray(struct.pack(">I", len(plainbytes)))
        for plainbyte in plainbytes:
            cipherbyte = key ^ plainbyte
            key = cipherbyte
            buffer.append(cipherbyte)
        return bytes(buffer)

    def _decrypt(self, string):
        key = 0xAB
        buffer = []
        for cipherbyte in string:
            plainbyte = key ^ cipherbyte
            key = cipherbyte
            buffer.append(plainbyte)
        plaintext = bytes(buffer)
        return plaintext.decode()

    def _write_command(self, encrypted_command):
        self._verify_socket_connected()
        self.sock.sendall(encrypted_command)
        data = self.sock.recv(4096)
        return self._decrypt(data[4:])

    def _verify_socket_connected(self):
        if self.sock is None:
            raise Exception('Socket not connected!')

    def connect(self):
        # Disconnect first, if connected
        self.disconnect()
        # Connect
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip, self.port))
        except Exception as e:
            self.sock = None
            raise e

    def disconnect(self):
        if self.sock is not None:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.sock = None

    def get_info(self):
        data = self._write_command(self.COMMANDS['info'])
        json_data = json.loads(data)
        return json_data

    def get_time(self):
        data = self._write_command(self.COMMANDS['time'])
        json_data = json.loads(data)
        return json_data

    def get_energy(self):
        data = self._write_command(self.COMMANDS['energy'])
        json_data = json.loads(data)
        return json_data

    def set_on(self):
        data = self._write_command(self.COMMANDS['on'])
        json_data = json.loads(data)
        return json_data

    def set_off(self):
        data = self._write_command(self.COMMANDS['off'])
        json_data = json.loads(data)
        return json_data

    def set_led_off(self):
        data = self._write_command(self.COMMANDS['led_off'])
        json_data = json.loads(data)
        return json_data

    def set_led_on(self):
        data = self._write_command(self.COMMANDS['led_on'])
        json_data = json.loads(data)
        return json_data