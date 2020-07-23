from pathlib import Path
import pylexibank

from clldutils.misc import slug

from pylexibank.util import getEvoBibAsBibtex


# Customize your basic data.
# if you need to store other data in columns than the lexibank defaults, then over-ride
# the table type (pylexibank.[Language|Lexeme|Concept|Cognate|]) and add the required columns e.g.
#
# import attr
#
# @attr.s
# class Concept(pylexibank.Concept):
#    MyAttribute1 = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "chacontukanoan"

    # register custom data types here (or language_class, lexeme_class, cognate_class):
    # concept_class = Concept

    # define the way in which forms should be handled
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,",  # characters that split forms e.g. "a, b".
        missing_data=('?', '-'),  # characters that denote missing data.
        strip_inside_brackets=True
        # do you want data removed in brackets or not?
    )

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.
        to download a temporary TSV file and convert to persistent CSV:

        >>> with self.raw_dir.temp_download("http://www.example.com/e.tsv", "example.tsv") as data:
        ...     self.raw_dir.write_csv('template.csv', self.raw_dir.read_csv(data, delimiter='\t'))
        """
        with self.raw_dir.temp_download(
                "http://edictor.digling.org/triples/get_data.py?file=tukano",
                "tukano.tsv") as data:
            self.raw_dir.write_csv('tukano.csv',
                                   self.raw_dir.read_csv(data, delimiter='\t'))
        self.raw_dir.write('sources.bib', getEvoBibAsBibtex('Chacon2014'))

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        A `pylexibank.cldf.LexibankWriter` instance is available as `args.writer`. Use the methods
        of this object to add data.
        """
        data = self.raw_dir.read_csv('tukano.csv', dicts=True)

        args.writer.add_sources()
        # short cut to add concepts and languages, provided your name spaces
        # match lexibank's expected format.
        # args.writer.add_concepts()
        args.writer.add_languages()

        # if not, then here is a more detailed way to do it:
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

        # for language in self.languages:
        #    args.writer.add_language(
        #        ID=language['ID'],
        #        Glottolog=language['Glottolog']
        #    )

        # add data
        for row in pylexibank.progressbar(data):
            # .. if you have segmentable data, replace `add_form` with `add_form_with_segments`
            # .. TODO @Mattis, when should we use add_forms_from_value() instead?

            # '*PT' is an illegal identifier, changed to 'ProtoT'
            if row['DOCULECT'] == "*PT":
                row['DOCULECT'] = "ProtoT"

            c_id = concept_lookup[row['CONCEPT']]
            lex = args.writer.add_form_with_segments(
                Language_ID=row['DOCULECT'],
                Parameter_ID=c_id,
                Value=row['IPA'],
                Form=row['IPA'],
                Segments=row['TOKENS'].split(),
                Source=['Chacon2014'],
            )
            # add cognates -- make sure Cognateset_ID is global!
            args.writer.add_cognate(
                lexeme=lex,
                Cognateset_ID='{0}-{1}'.format(c_id, row['COGID'])
            )
