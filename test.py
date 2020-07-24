def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    num_forms = len(list(cldf_dataset["FormTable"]))
    expected_forms = 1542
    assert num_forms == expected_forms, \
        "This dataset should have {} forms, found {}".format(expected_forms,
                                                             num_forms)


def test_cognates(cldf_dataset):
    cog_table = cldf_dataset["CognateTable"]
    num_cognates = len(list(cog_table))
    expected_cognates = 1542
    assert num_cognates == expected_cognates, \
        "This dataset should have {} cognates, found {}".format(num_cognates,
                                                                expected_cognates)


def test_alignments(cldf_dataset):
    """Test the integrity of the alignments.

    The alignments should:
    - Have a fixed number of columns for a given cognate set
    - Not contain the character �, which signals a segmentation error
    - Have the same segments as the corresponding form
    """
    cog_table = cldf_dataset["CognateTable"]
    forms = {r["ID"]: r["Segments"] for r in cldf_dataset["FormTable"]}
    alignment_lengths = {}
    for row in cog_table:
        alignment = row["Alignment"]
        assert "�" not in alignment, "Segmentation error in {} (at form ID: {})" \
            .format(alignment, form_id)
        id = row["Cognateset_ID"]
        length = len(alignment)
        if id in alignment_lengths:
            assert alignment_lengths[id] == length, \
                "Invalid alignment length  (at cognateset ID: {} for cognate {})" \
                .format(id, row["ID"])
        else:
            alignment_lengths[id] = length
        form_id = row["Form_ID"]
        segmented = forms[form_id]
        stripped_alignment = [s for s in alignment if s not in "-()"]
        assert stripped_alignment == segmented, \
            "The alignment and the form should not have different segments (at form ID: {})" \
            .format(form_id)


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
