def test_get_recipes_with_empty_database(client):
	result = client.get("/recipes")
	assert not result.json['success']
	assert result.json['code'] == 404

def test_add_correct_recipe(client):
	result = client.post('/addrecipe', json={
		'password': 'Troglodon5986',
		'name': 'testrecipe',
		'servings': 2,
		'description': 'This is a test recipe',
		'ingredients': [
			{'name': 'testIngredient',
			'amount': 1,
			'unit': 'dl'}
		],
		'instructions': [
			{'step': 1,
			'instruction': 'This is just a test, nothing to really do'}
		]
	})
	assert result.json['success']
	assert result.json['code'] == 201

def test_get_all_data(client):
	result = client.get("/")
	assert result.json['success']
	assert result.json['code'] == 200
	assert result.json['result']['recipes']

def test_get_all_recipes(client):
	result = client.get("/recipes")
	assert result.json['success']
	assert result.json['code'] == 200
	assert len(result.json['result'])

def test_add_recipe_without_password(client):
	result = client.post('/addrecipe', json={
		'name': 'testrecipe2',
		'servings': 2,
		'description': 'This is another test recipe',
		'ingredients': [
			{'name': 'testIngredient',
			'amount': 1,
			'unit': 'dl'}
		],
		'instructions': [
			{'step': 1,
			'instruction': 'This is again just a test, nothing to really do'}
		]
	})
	assert not result.json['success']
	assert result.json['code'] == 401

def test_edit_recipe(client):
	result = client.put('/editrecipe', json={
		'password': 'Troglodon5986',
		'name': 'testrecipe',
		'recipe': {
			'name': 'testrecipe',
			'servings': 2,
			'description': 'This is the edited test recipe',
			'ingredients': [
				{'name': 'testIngredient',
				'amount': 1,
				'unit': 'dl'}
			],
			'instructions': [
			{'step': 1,
			'instruction': 'This is still just a test, nothing to really do'}
		]
		}
	})
	assert result.json['success']
	assert result.json['code'] == 200

def test_remove_recipe(client):
	result = client.put('/removerecipe', json={
	'password': 'Troglodon5986',
	'name': 'testrecipe'
	})
	assert result.json['success']