def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    num_forms = len(list(cldf_dataset["FormTable"]))
    expected_forms = 1542
    assert num_forms == expected_forms, \
        "This dataset should have {} forms, found {}".format(expected_forms,
                                                             num_forms)


def test_parameters(cldf_dataset):
    num_concepts = len(list(cldf_dataset["ParameterTable"]))
    expected_concepts = 142
    assert num_concepts == expected_concepts, \
        "This dataset should have {} concepts, found {}".format(
            expected_concepts, num_concepts)


def test_languages(cldf_dataset):
    num_languages = len(list(cldf_dataset["LanguageTable"]))
    expected_languages = 16
    assert num_languages == expected_languages, \
        "This dataset should have {} languages, found {}".format(
            expected_languages, num_languages)
