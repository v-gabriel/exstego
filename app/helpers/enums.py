from enum import Enum


# region Universal
class ToolProcesses:
    def __init__(self, tool, processes):
        self.tool = tool
        self.processes = processes


class FileOriginType(Enum):
    STEGO = "Stego file"
    ORIGINAL = "Original file"


class AttackOption(Enum):
    BIT_PLANES_SPLIT = "Split bit planes of stego file"
    BIT_PLANES_COMPARE = "Compare bit planes of the original and stego file"
    BIT_PLANES_OVERLAP = "Overlap bit planes of stego file"

    LSB_DESTROY_ATTACK = "Scramble data hidden in LSBs"
    LSB_EXTRACTION = "Extract data hidden in LSBs"
    HISTOGRAM_ANALYSIS = "Compare histograms of two images"

    METADATA_DESTRUCTION = "Destroy all metadata"
    METADATA_EXTRACTION = "Extract metadata"


class ColorType(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


class AttackModule(Enum):
    SPECIFIC = 'Attack specific techniques'
    CUSTOM = 'Customize all available attacks'

    # TODO: update desc
    @classmethod
    def get_markup_description(cls, value):
        match value:
            case cls.SPECIFIC.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.ATTACK_MODULE_SPECIFIC_DESCRIPTION.value}"
            case cls.CUSTOM.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.ATTACK_MODULE_CUSTOM_DESCRIPTION.value}"
            case _:
                return "No description available"


class EmbedOption(Enum):
    LSB = 'Use the LSB technique to hide data'
    METADATA = 'Hide data in file metadata'

    # TODO: update desc
    @classmethod
    def get_markup_description(cls, value):
        match value:
            case cls.LSB.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.EMBED_LSB_DESCRIPTION.value}"
            case cls.METADATA.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.EMBED_METADATA_DESCRIPTION.value}"
            case _:
                return "No description available"


class StegoTechnique(Enum):
    LSB = 'Least significant bit steganography'
    BPCS = 'Bit plane complexity segmentation steganography'
    METADATA = 'Metadata steganography'

    # TODO: update desc
    @classmethod
    def get_markup_description(cls, value):
        match value:
            case cls.LSB.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.ATTACK_LSB_DESCRIPTION.value}"
            case cls.BPCS.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.ATTACK_BPCS_DESCRIPTION.value}"
            case cls.METADATA.value:
                return f"[b]{value}[/b]\n" \
                       f"{Text.ATTACK_METADATA_DESCRIPTION.value}"
            case _:
                return "No description available"
# endregion


# region BPCS analyzer
class BPCSAnalyzerParams(Enum):
    COLOR_CHANNELS = "Color channels to use"
    BIT_PLANES_TO_KEEP = "Bit planes to keep"


class BPCSAnalyzerResults:
    bit_planes_per_channel = {FileOriginType.ORIGINAL.value:
                                  {ColorType.RED.value: [],
                                   ColorType.GREEN.value: [],
                                   ColorType.BLUE.value: []},
                              FileOriginType.STEGO.value:
                                  {ColorType.RED.value: [],
                                   ColorType.GREEN.value: [],
                                   ColorType.BLUE.value: []}
                              }

    planes_overlap_image = {FileOriginType.ORIGINAL.value: None,
                            FileOriginType.STEGO.value: None}
# endregion


# region LSB handler
class LSBEmbedPixelOption(Enum):
    SEQUENTIAL = "Sequential"
    SCATTER = "Scatter"


class LSBHandlerParams(Enum):
    EMBED_OPTION = "Embed option"
    PERCENTAGE_TO_COVER = "File percentage to take"
    COLORS_TO_USE = "Colors to use"
    MESSAGE_TO_HIDE = "Message to hide"


class LSBHandlerResults:
    hidden_image_source = None
    destroyed_image_source = None

    extracted_text = None
# endregion


# region Histogram analyzer
class HistogramAnalyzerResults:
    equality_percentage = None
    histogram_src = {FileOriginType.ORIGINAL.value: None,
                     FileOriginType.STEGO.value: None}
# endregion


# region Metadata handler
class MetadataTypes(Enum):
    XMP = "XMP tags"
    EXIF = "EXIF tags"
    IPTC = "IPTC tags"
    COMMENT = "Comment"


class MetadataFileChangeType(Enum):
    ALTERED = "Altered"
    DESTROYED = "Destroyed"
    ORIGINAL = "Original"


class MetadataHandlerParams(Enum):
    METADATA_KEY = "Metadata key"


class MetadataHandlerResults:
    destroyed_tags = {MetadataTypes.XMP.value: None,
                      MetadataTypes.EXIF.value: None,
                      MetadataTypes.IPTC.value: None,
                      MetadataTypes.COMMENT.value: None}

    edited_tags = {MetadataTypes.XMP.value: None,
                   MetadataTypes.EXIF.value: None,
                   MetadataTypes.IPTC.value: None,
                   MetadataTypes.COMMENT.value: None}

    original_tags = {MetadataTypes.XMP.value: None,
                     MetadataTypes.EXIF.value: None,
                     MetadataTypes.IPTC.value: None,
                     MetadataTypes.COMMENT.value: None}
# endregion


# region ui handling
class Text(Enum):
    __backslash = '\n'
    HOME_PAGE_DESCRIPTION = f"Embed data or attack files through available methods.\n" \
                            f"Attacks can analyze, extract or destroy data.\n" \
                            f"Data and logs are saved relative to the root folder of the app: [i]./RESULTS/…[/i]\n" \

    ATTACK_MODULE_SPECIFIC_DESCRIPTION = f"- Dependant on the technique used\n" \
                                         f"- Data is saved relative to the root folder of the app: [i]./RESULTS/…[/i]\n" \
                                         f"- [u]Available techniques[/u]:\n" \
                                         f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in StegoTechnique])}\n"

    ATTACK_LSB_DESCRIPTION = f"- Destroy/ extract data hidden in LSBs\n" \
                             f"- [u]Available parameters[/u]:\n" \
                             f"- Colors:\n" \
                             f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in ColorType])}\n" \
                             f"- Embed options:\n" \
                             f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in EmbedOption])}\n" \
                             f"- Percentage to cover\n"

    ATTACK_METADATA_DESCRIPTION = f"- Extract or scramble available metadata tags\n"

    ATTACK_BPCS_DESCRIPTION = f"- Extract, overlap or compare bit planes\n" \
                              f"- [u]Available parameters[/u]:\n" \
                              f"- Colors:\n" \
                              f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in ColorType])}\n" \
                              f"- Bit planes:\n" \
                              f"    - {[i+1 for i in range(8)]}\n" \

    EMBED_METADATA_DESCRIPTION = f"- Hide messages in given metadata tags\n"

    EMBED_LSB_DESCRIPTION =  f"- Embed data in LSBs\n" \
                             f"- [u]Available parameters[/u]:\n" \
                             f"- Colors:\n" \
                             f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in ColorType])}\n" \
                             f"- Embed options:\n" \
                             f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in EmbedOption])}\n" \
                             f"- Percentage to cover\n" \
                             f"- Message to embed\n"

    ATTACK_MODULE_CUSTOM_DESCRIPTION = f"- Combine all available attacks\n" \
                                       f"- Data is saved relative to the root folder of the app: [i]./RESULTS/…[/i]\n" \
                                       f"- [u]Available attacks[/u]:\n" \
                                       f"{f'{__backslash}'.join([f'  - {enum.value}' for enum in AttackOption])}"

    EMPTY_VALUE = "No value selected..."
    EMPTY_FILE = "No file selected..."

    ANALYSIS_ATTACKS_UNAVAILABLE = "This method is currently unavailable." \
                                   "\nPlease provide both the original and stego file."
    STEGO_FILE_ATTACKS_UNAVAILABLE = "This method is currently unavailable." \
                                     "\nPlease provide the stego file."

    DIALOG_TITLE_NOT_AVAILABLE = "Not available"
    DIALOG_TITLE_NO_OPTION_SELECTED = "No option selected"
    DIALOG_PROVIDE_OPTION = "Please select an option."

    METADATA_TAGS_NOTE_EXTRACTION_DESCRIPTION = \
        "[color=3D3D3D]Note! \n" \
        "Check [u][color=478BC2][ref=https://exiv2.org/metadata.html]link[/ref][/color][/u] for available tags.\n" \
        "Format: {metadata_type}.{namespace}.{tag}\n" \
        "Use new line (enter) for each new tag. Leave blank to read all existing tags."

    METADATA_TAGS_NOTE_EMBEDDING_DESCRIPTION = \
        "[color=3D3D3D]Note! \n" \
        "Check [u][color=478BC2][ref=https://exiv2.org/metadata.html]link[/ref][/color][/u] for available tags.\n" \
        "Format: {metadata_type}.{namespace}.{tag}:{value}\n" \
        "Xmp supports custom tags, example: Xmp.dc.{custom_tag}\n" \
        "Use new line (enter) for each new tag. Leave blank to read all existing tags."


class Selection(Enum):
    SELECTED = "checkbox-marked"
    UNSELECTED = "checkbox-blank-outline"


class ScreenNames(Enum):
    HOME_PAGE = "homePage"

    # Attack
    CHOOSE_ATTACK_MODULE_PAGE = "chooseAttackModulePage"

    ATTACK_SPECIFIC_TECHNIQUE_PAGE = "attackSpecificTechniquePage"
    ATTACK_LSB_TECHNIQUE_PAGE = "attackLSBTechniquePage"
    ATTACK_BPCS_TECHNIQUE_PAGE = "attackBPCSTechniquePage"
    ATTACK_METADATA_TECHNIQUE_PAGE = "attackMETADATATechniquePage"

    CUSTOM_ATTACKS_PAGE = "customAttacksPage"

    CUSTOMIZE_SELECTED_ATTACKS_PAGE = "customizeSelectedAttacksPage"
    ATTACKS_LOADING_PAGE = "attacksLoadingPage"
    ATTACKS_RESULTS_PAGE = "attacksResultsPage"

    # Embed
    CHOOSE_EMBED_OPTION_PAGE = "chooseEmbedOptionPage"
    EMBED_LSB_PAGE = "embedLSBPage"
    EMBED_METADATA_PAGE = "embedMETADATAPage"
    EMBEDDING_LOADING_PAGE = "embeddingLoadingPage"
    EMBEDDING_RESULTS_PAGE = "embeddingResultsPage"
    EMBEDDING_ERROR_PAGE = "embeddingErrorPage"
# endregion
