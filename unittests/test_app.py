def test_get_all_data(client):
    result = client.get("/")
    assert result.json['success']
    assert result.json['code'] == 200

def test_get_all_recipes(client):
    result = client.get("/")
    assert result.json['success']
    assert result.json['code'] == 200