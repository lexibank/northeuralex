import attr
from pathlib import Path
from clldutils.misc import slug
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Lexeme, Language
from pylexibank.util import pb


@attr.s
class NLLexeme(Lexeme):
    Orthography = attr.ib(default=None)


@attr.s
class NLLanguage(Language):
    Subfamily = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "northeuralex"
    lexeme_class = NLLexeme
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
        def concept_id(s):
            return slug(
                s.replace(":", "_").replace("[", "-").replace("]", "-"), lowercase=False
            )

        # add the bibliographic sources
        args.writer.add_sources()

        # add the languages from the language list (no need for mapping here)
        args.writer.add_languages()

        # add the concepts from the concept list
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda c: "%s_%s" % (c.id.split("-")[-1],
                slug(c.english)),
            lookup_factory="Name")

        # add items
        lexeme_rows = self.raw_dir.read_csv("nelex.tsv", delimiter="\t", dicts=True)
        for row in pb(lexeme_rows, desc=f"Build CLDF for {self.id}"):
            lex = args.writer.add_form(
                Language_ID=row["Language_ID"],
                Parameter_ID=concept_lookup[row["Concept_ID"]],
                Value=row["rawIPA"],
                Form=row["rawIPA"],
                Orthography=row["Word_Form"],
                Source=[],
            )
