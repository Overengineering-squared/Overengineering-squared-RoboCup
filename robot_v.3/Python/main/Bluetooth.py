import struct

import serial


class Bluetooth:
    def __init__(self, debug=False):
        self.__bluetooth = serial.Serial('/dev/rfcomm0')
        self.__debug = debug

    def send_message(self, text_to_send):
        data = self.__encode_message("abc", text_to_send)

        if self.__debug:
            print('Sending message: ', self.__print_message(data))

        self.__bluetooth.write(data)

    def receive_message(self):
        if self.__bluetooth.in_waiting > 0:
            data = self.__bluetooth.read(self.__bluetooth.in_waiting)

            if self.__debug:
                print(data)

            text = self.__decode_message(data)

            if self.__debug:
                print(text)

            return text
        else:
            return None

    @staticmethod
    def __encode_message(mail_name, text_to_send):
        mail_name += '\x00'
        mail_bytes = mail_name.encode('ascii')
        mail_size = len(mail_bytes)
        fmt = '<H4BB' + str(mail_size) + 'sH'

        text_to_send += '\x00'
        value_bytes = text_to_send.encode('ascii')
        value_size = len(value_bytes)
        fmt += str(value_size) + 's'

        payload_size = 7 + mail_size + value_size
        data = struct.pack(fmt, payload_size, 0x01, 0x00, 0x81, 0x9e, mail_size, mail_bytes, value_size, value_bytes)
        return data

    @staticmethod
    def __decode_message(data):
        mail_size = struct.unpack_from('<B', data, 6)[0]

        text_bytes = struct.unpack_from('<' + str(mail_size) + 's', data, 7)[0]
        text = text_bytes.decode('ascii')[:-1]

        return text

    @staticmethod
    def __print_message(message_bytes):
        return ''.join(f"{byte:02x}" for byte in message_bytes)
