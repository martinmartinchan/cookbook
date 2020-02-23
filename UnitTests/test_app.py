def test_index(client):
    result = client.get("/")
    print(result.json)
    assert result.json['success']