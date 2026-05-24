from pydantic import Field
from pydantic.alias_generators import to_pascal
from pydantic_settings import BaseSettings, SettingsConfigDict

class PaletteColors(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.config',
        env_prefix='PALETTE_',
        extra='ignore'
    )

    PRIMARY: str
    SECONDARY: str
    SUCCESS: str
    DANGER: str
    WARNING: str
    BG: str
    CARD: str
    TEXT: str
    MUTED: str


class SegmentColors(BaseSettings):
    model_config = SettingsConfigDict(
        alias_generator=to_pascal,
        env_file='.config',
        env_prefix='SEGMENT_',
        extra='ignore',
        populate_by_name=True
    )
    PREMIUM: str
    STANDARD: str
    BUDGET: str


class CategoryColors(BaseSettings):
    model_config = SettingsConfigDict(
        alias_generator=to_pascal,
        env_file='.config',
        env_prefix='CATEGORY_',
        extra='ignore',
        populate_by_name=True
    )

    ELECTRONICS: str
    CLOTHING: str
    HOME: str = Field(validation_alias='CATEGORY_HOME')
    BOOKS: str
    SPORTS: str


palette_colors = PaletteColors()
segment_colors = SegmentColors()
category_colors = CategoryColors()
