# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.dsv import NamedTupleReader
import attr

from clldutils.path import Path
from clldutils.misc import slug
from pylexibank.dataset import Metadata, Lexeme, Language
from pylexibank.dataset import Dataset as BaseDataset

from pylexibank.util import pb


@attr.s
class NLLexeme(Lexeme):
    Orthography = attr.ib(default=None)


@attr.s
class NLLanguage(Language):
    Subfamily = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = 'northeuralex'
    lexeme_class = NLLexeme
    language_class = NLLanguage

    def cmd_download(self, **kw):
        self.raw.download(
            'http://www.northeuralex.org/static/downloads/northeuralex-cldf.csv',
            "nelex.tsv",
            log=self.log)

    def split_forms(self, row, value):
        """
        We make sure to always only yield one form per raw lexeme.
        """
        return BaseDataset.split_forms(self, row, value)[:1]

    def cmd_install(self, **kw):
        def concept_id(s):
            return slug(
                s.replace(':', '_').replace('[', '-').replace(']', '-'),
                lowercase=False)

        with self.cldf as ds, NamedTupleReader(
                self.raw.posix('nelex.tsv'), delimiter="\t") as reader:
            ds.add_sources()
            ds.add_languages()
            ds.add_concepts(id_factory=lambda c: concept_id(c.attributes['nelex_id']))

            for row in pb(reader, desc="installing northeuralex"):
                if row.rawIPA:
                    ds.add_lexemes(
                        Language_ID=row.Language_ID,
                        Parameter_ID=concept_id(row.Concept_ID),
                        Value=row.rawIPA,
                        Orthography=row.Word_Form,
                        Source=[],
                    )

