# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.dsv import NamedTupleReader
import attr

from clldutils.path import Path
from clldutils.misc import slug
from pylexibank.dataset import Metadata, Lexeme
from pylexibank.dataset import Dataset as BaseDataset

from pylexibank.util import pb


@attr.s
class NLLexeme(Lexeme):
    Orthography = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    lexeme_class = NLLexeme
    id = "northeuralex"

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
        ccode = {x.attributes['nelex_id']: x.concepticon_id for x in
                 self.conceptlist.concepts.values()}

        with self.cldf as ds, NamedTupleReader(
                self.raw.posix('nelex.tsv'), delimiter="\t") as reader:
            ds.add_sources(self.raw.read('sources.bib'))

            for row in pb(reader, desc="installing northeuralex"):
                cid = row.Concept_ID.replace(':', '_').replace('[', '-').replace(']', '-') if row.Concept_ID else None
                cid = slug(cid, lowercase=False)
                if row.rawIPA:
                    ds.add_language(
                        ID=row.Language_ID,
                        Name=row.Language_ID,
                        Glottocode=row.Glottocode)
                    ds.add_concept(
                        ID=cid,
                        Name=row.Concept_ID,
                        Concepticon_ID=ccode[row.Concept_ID])
                    ds.add_lexemes(
                        Language_ID=row.Language_ID,
                        Parameter_ID=cid,
                        Value=row.rawIPA,
                        Orthography=row.Word_Form,
                        Source=[],
                        Segments=self.tokenizer(None, row.rawIPA, column='IPA'))

