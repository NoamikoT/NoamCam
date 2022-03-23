

def unpack(message):

    code = message[:2]

    unpacked_message = ""

    data = message[2:]

    return unpacked_message


def build_face_recognition(status):

    code = "01"

    packed_message = code + status

    return packed_message


def build_siren():

    code = "02"

    return code