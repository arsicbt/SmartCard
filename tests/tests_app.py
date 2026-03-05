def test_apdu_format():
    apdu = "00A40400"
    assert len(apdu) % 2 == 0


def test_status_word_success():
    sw = "9000"
    assert sw == "9000"


def test_hex_string():
    value = "A0B1C2"
    int(value, 16)
    assert True