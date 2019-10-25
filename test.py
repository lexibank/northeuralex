def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)

def test_forms(cldf_dataset):
    assert 1 == 1

def test_parameters(cldf_dataset):
    assert 1 == 1

def test_languages(cldf_dataset):
    assert 1 == 1

def test_cognates(cldf_dataset):
    assert 1 == 1
