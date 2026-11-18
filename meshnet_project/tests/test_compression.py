from meshnet.compression import compress_payload, decompress_payload


def test_small_payload_roundtrip():
    data = b"hi"
    packed = compress_payload(data)
    assert decompress_payload(packed) == data


def test_large_payload_roundtrip():
    data = b"hello-mesh-" * 200
    packed = compress_payload(data)
    assert decompress_payload(packed) == data
