from meshnet.port_selection import is_prime, nearest_prime_port, reserve_udp_port


def test_prime_detection():
    assert is_prime(2)
    assert is_prime(3)
    assert is_prime(49157)
    assert not is_prime(1)
    assert not is_prime(4)
    assert not is_prime(49152)


def test_nearest_prime_port_in_dynamic_range():
    p = nearest_prime_port(50000)
    assert is_prime(p)
    assert 49152 <= p <= 65535


def test_os_assigned_udp_port_default():
    sock, port = reserve_udp_port(host="127.0.0.1", prefer_prime=False)
    try:
        assert isinstance(port, int)
        assert 1 <= port <= 65535
    finally:
        sock.close()
