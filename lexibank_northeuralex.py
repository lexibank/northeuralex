import attr
from pathlib import Path
from clldutils.misc import slug
import pylexibank


@attr.s
class CustomLexeme(pylexibank.Lexeme):
    Orthography = attr.ib(default=None)


@attr.s
class CustomConcept(pylexibank.Concept):
    NorthEuralex_Gloss = attr.ib(default=None)


@attr.s
class CustomLanguage(pylexibank.Language):
    Subfamily = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Latitude = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "northeuralex"
    lexeme_class = CustomLexeme
    concept_class = CustomConcept
    language_class = CustomLanguage
    form_spec = pylexibank.FormSpec(replacements=[(" ", "_"), ("_..._", "-")])

    def cmd_download(self, args):
        self.raw_dir.download(
            "http://www.northeuralex.org/static/downloads/northeuralex-cldf.csv", "nelex.tsv"
        )

    def cmd_makecldf(self, args):
        # add the bibliographic sources
        args.writer.add_sources()

        # add the languages from the language list (no need for mapping here)
        args.writer.add_languages()

        # add the concepts from the concept list
        concept_lookup = {}
        for concept in self.conceptlists[0].concepts.values():
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
        for row in pylexibank.progressbar(lexeme_rows):
            args.writer.add_form(
                Language_ID=row["Language_ID"],
                Parameter_ID=concept_lookup[row["Concept_ID"]],
                Value=row["Word_Form"],
                Form=row["rawIPA"].strip().replace(" ", "_"),
                Source=["Dellert2020"],
            )
