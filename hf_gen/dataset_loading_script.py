import datasets
import json

SB_CONFIGURATION = json.load("sb_config.json")

__URL = SB_CONFIGURATION["__URL"]
__DESCRIPTION = SB_CONFIGURATION["__DESCRIPTION"]
__CITATION = SB_CONFIGURATION["__CITATION"]
_HOMEPAGE = SB_CONFIGURATION["__HOMEPAGE"]

class Config(datasets.BuilderConfig):
    """BuilderConfig for Config."""

    def __init__(self, period="all", **kwargs):
        """Constructs a kubhist2Dataset.
        Args:
        period: can be any key in _URLS, `all` takes all
        **kwargs: keyword arguments forwarded to super.
        """
        super(Config, self).__init__(**kwargs)


class Builder(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIG_CLASS = Config
    BUILDER_CONFIGS = []

    def _info(self):
        f = datasets.Features({
            "sentence": datasets.Value("string")
        })

        return datasets.DatasetInfo(
            features=f,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=__CITATION,
        )

    def _split_generators(self, dl_manager):
        raise NotImplementedError        

    def _generate_examples(self, filepath):
        raise NotImplementedError