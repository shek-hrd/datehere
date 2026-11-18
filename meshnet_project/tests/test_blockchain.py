from meshnet.blockchain import MessageBlockchain


def test_genesis_and_append_and_verify():
    bc = MessageBlockchain()
    assert len(bc.chain) == 1
    assert bc.chain[0]["index"] == 0
    assert bc.chain[0]["prev_hash"] == "0" * 64
    assert bc.verify()

    b1 = bc.append({"id": "m1", "kind": "chat", "source": "a", "payload": "hi", "created_at": 1.0, "path": ["a", "b"], "hops": 1})
    b2 = bc.append({"id": "m2", "kind": "system", "source": "b", "payload": "HAIL", "created_at": 2.0, "path": ["b"], "hops": 0})
    assert b1["index"] == 1 and b2["index"] == 2
    assert b1["prev_hash"] == bc.chain[0]["hash"]
    assert b2["prev_hash"] == b1["hash"]
    assert b2["hash"] == bc.head["hash"]
    assert bc.verify()


def test_tamper_detected():
    bc = MessageBlockchain()
    bc.append({"id": "m1", "kind": "chat", "source": "a", "payload": "hi", "created_at": 1.0, "path": ["a"], "hops": 0})
    assert bc.verify()
    bc.chain[1]["payload"] = "tampered"
    assert not bc.verify()
