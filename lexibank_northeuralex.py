import attr
from pathlib import Path
from clldutils.misc import slug
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Lexeme, Concept, Language
from pylexibank.util import progressbar


@attr.s
class NLLexeme(Lexeme):
    Orthography = attr.ib(default=None)


@attr.s
class NLConcept(Concept):
    NorthEuralex_Gloss = attr.ib(default=None)


@attr.s
class NLLanguage(Language):
    Subfamily = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Latitude = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "northeuralex"
    lexeme_class = NLLexeme
    concept_class = NLConcept
    language_class = NLLanguage

    def cmd_download(self, args):
        self.raw_dir.download(
            "http://www.northeuralex.org/static/downloads/northeuralex-cldf.csv",
            "nelex.tsv",
            log=self.log,
        )

    def split_forms(self, row, value):
        """
        We make sure to always only yield one form per raw lexeme.
        """
        return BaseDataset.split_forms(self, row, value)[:1]

    def cmd_makecldf(self, args):
        # add the bibliographic sources
        args.writer.add_sources()

        # add the languages from the language list (no need for mapping here)
        args.writer.add_languages()

        # add the concepts from the concept list
        concept_lookup = {}
        for concept in self.conceptlist.concepts.values():
            cid = "%s_%s" % (concept.id.split("-")[-1], slug(concept.english))
            args.writer.add_concept(
                ID=cid,
                Name=concept.english,
                NorthEuralex_Gloss=concept.attributes["nelex_id"],
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )
            concept_lookup[concept.attributes["nelex_id"]] = cid

        # add items
        lexeme_rows = self.raw_dir.read_csv("nelex.tsv", delimiter="\t", dicts=True)
        for row in progressbar(lexeme_rows):
            lex = args.writer.add_form(
                Language_ID=row["Language_ID"],
                Parameter_ID=concept_lookup[row["Concept_ID"]],
                Value=row["Word_Form"],
                Form=row["rawIPA"],
                Source=["Dellert2017"],
            )
