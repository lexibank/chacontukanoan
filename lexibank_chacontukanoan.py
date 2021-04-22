from pathlib import Path

import pylexibank
from clldutils.misc import slug
from pylexibank.util import getEvoBibAsBibtex
from segments import Tokenizer


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "chacontukanoan"

    def cmd_download(self, args):
        with self.raw_dir.temp_download(
            "http://edictor.digling.org/triples/get_data.py?file=tukano", "tukano.tsv"
        ) as data:
            self.raw_dir.write_csv("tukano.csv", self.raw_dir.read_csv(data, delimiter="\t"))
        self.raw_dir.write("sources.bib", getEvoBibAsBibtex("Chacon2014"))

    def cmd_makecldf(self, args):
        data = self.raw_dir.read_csv("tukano.csv", dicts=True)
        args.writer.add_sources()

        # Get our own tokenizer from the orthography profile
        # because of multi-profile support, the orthography profile dict
        # has a single item, keyed by `None`.
        tokenizer = Tokenizer(profile=self.orthography_profile_dict[None])

        def _re_tokenize(segmented):
            """ Generator of re-tokenized sequences.

            Used to re-tokenize alignments, which is needed due to changes
            in the orthography profile

            Args:
                segmented: list of strings

            Generates: tokenized segments
            """
            preserve_chars = {"(", ")", "-"}
            for seg in segmented:
                if seg in preserve_chars:
                    yield seg
                else:
                    normalized = self.form_for_segmentation(seg)
                    tokenized = tokenizer(normalized, column="IPA")
                    for seg in tokenized.split(" "):
                        yield seg

        concept_lookup = {}
        for concept in self.conceptlists[0].concepts.values():
            c_id = "{0}-{1}".format(concept.id.split("-")[-1], slug(concept.english))
            concept_lookup[concept.english] = c_id
            args.writer.add_concept(
                ID=c_id,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
                Name=concept.english,
            )

        language_lookup = {}
        for language in self.languages:
            args.writer.add_language(
                ID=language["ID"], Glottocode=language["Glottocode"], Name=language["Name"]
            )
            language_lookup[language["ID_in_raw"]] = language["ID"]

        # add data
        for row in pylexibank.progressbar(data):
            language_id = language_lookup[row["DOCULECT"]]
            c_id = concept_lookup[row["CONCEPT"]]

            # The alignments were corrected by hand,
            # when they differ from the segments,
            # the correct notation is in the alignments
            tokens = row["TOKENS"].split()
            alignment = row["ALIGNMENT"].split(" ")
            stripped_alignments = [s for s in alignment if s not in {"(", "-", ")"}]
            if tokens != stripped_alignments:
                tokens = stripped_alignments

            lex = args.writer.add_form(
                Language_ID=language_id,
                Parameter_ID=c_id,
                Value=row["IPA"],
                # This is a workaround to re-tokenize tokens
                Form=".".join(tokens),
                Source=["Chacon2014"],
            )

            # add cognates -- make sure Cognateset_ID is global!
            args.writer.add_cognate(
                lexeme=lex,
                Cognateset_ID="{0}-{1}".format(c_id, row["COGID"]),
                Source=["Chacon2014"],
                Alignment=list(_re_tokenize(alignment)),
                Alignment_Method="expert",
                Alignment_Source="Chacon2014",
            )
