import multiprocessing
from multiprocessing import freeze_support
import os
import webbrowser
from copy import deepcopy
from datetime import date
from tkinter import filedialog, Label as TKLabel, Tk
import shortuuid
from helpers.enums import AttackOption, StegoTechnique, AttackModule, EmbedOption, Selection, Text as Text, \
    ScreenNames, FileOriginType, ColorType, BPCSAnalyzerParams, LSBHandlerParams, LSBEmbedPixelOption, ToolProcesses, \
    MetadataHandlerResults, HistogramAnalyzerResults, LSBHandlerResults, MetadataHandlerParams, BPCSAnalyzerResults
from helpers.logger import MessageHelper
from tools.bit_plane_analyzer import BitPlaneAnalyzer
from tools.histogram_analyzer import HistogramAnalyzer
from tools.lsb_handler import LSBHandler
from tools.metadata_handler import MetadataHandler

# ================================================================================================================
# NOTES:
#
# - kivy imports are located after freeze_support() due to a multiprocessing bug
# - it 'protects' a new process from opening kivy windows while doing background work
# - only available workaround atm
# ================================================================================================================

# Tkinter used as a file opener
tk = Tk()
tk.iconbitmap(default="./resources/transparent.ico")
lab = TKLabel(tk, text="Exstego")
lab.pack()

if __name__ == "__main__":
    freeze_support()

    # region Kivy imports
    from kivy import Config

    Config.set('graphics', 'width', '900')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'minimum_width', '900')
    Config.set('graphics', 'minimum_height', '600')

    from kivy.core.text import LabelBase
    from kivy.core.window import Window
    from kivymd.app import MDApp
    from kivy.uix.gridlayout import GridLayout
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivymd.uix.button import MDRectangleFlatIconButton, MDFlatButton, MDIconButton
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.label import MDLabel
    from kivymd.uix.list import OneLineListItem
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.gridlayout import MDGridLayout
    from kivy.uix.image import Image
    from kivy.metrics import dp
    from kivy.uix.widget import Widget
    from kivy.utils import rgba
    from kivy.uix.anchorlayout import AnchorLayout
    from kivymd.uix.menu import MDDropdownMenu
    from kivymd.uix.slider import MDSlider
    from kivy.uix.scrollview import ScrollView
    # endregion

    # region ui
    Builder.load_file('ui/Main/HomePage.kv')

    # Attack pages
    Builder.load_file('ui/Attack/ChooseAttackModulePage.kv')

    Builder.load_file('ui/Attack/AttackModules/CustomAttacksPage.kv')

    Builder.load_file('ui/Attack/AttackModules/AttackSpecificTechniquePage.kv')
    Builder.load_file('ui/Attack/AttackModules/SpecificTechniques/AttackLSBTechniquePage.kv')
    Builder.load_file('ui/Attack/AttackModules/SpecificTechniques/AttackBPCSTechniquePage.kv')
    Builder.load_file('ui/Attack/AttackModules/SpecificTechniques/AttackMETADATATechniquePage.kv')

    Builder.load_file('ui/Main/CustomizeSelectedAttacksPage.kv')
    Builder.load_file('ui/Main/AttacksLoadingPage.kv')
    Builder.load_file('ui/Main/AttacksResultsPage.kv')

    # Embed pages
    Builder.load_file('ui/Embed/ChooseEmbedOptionPage.kv')

    Builder.load_file('ui/Embed/EmbedOptions/EmbedLSBPage.kv')
    Builder.load_file('ui/Embed/EmbedOptions/EmbedMETADATAPage.kv')
    Builder.load_file('ui/Main/EmbeddingLoadingPage.kv')
    Builder.load_file('ui/Main/EmbeddingResultsPage.kv')
    Builder.load_file('ui/Main/EmbeddingErrorPage.kv')

    LabelBase.register(name="Montserrat",
                       fn_regular="./resources/Montserrat-Regular.ttf")


    class WindowManager(ScreenManager):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)


    class VerticalScroll(ScrollView):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)


    class HorizontalScrollView(ScrollView):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        # NOTE
        # override these 2 classes and delegate to parent
        # fixes the issue with horizontal scroll not working inside a vertical scroll
        # (ScrollView by x inside ScrollView by y)
        def on_scroll_start(self, touch, check_children=True):
            super().on_scroll_start(touch, check_children)

        def on_scroll_move(self, touch):
            super().on_scroll_move(touch)


    class Test(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.manager: WindowManager

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()


    class HomePage(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            self.ids.homePageDescription.text = Text.HOME_PAGE_DESCRIPTION.value


    class ChooseAttackModulePage(Screen):
        selectedAttackModule = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for module in AttackModule:
                tempWidget = OneLineListItem(text=f"{module.value}", on_release=self.on_specific_module_click)
                self.ids.attackModulesList.add_widget(tempWidget)

            del tempWidget

        def on_specific_module_click(self, item: OneLineListItem):
            self.selectedAttackModule = item.text
            self.ids.moduleInfo.text = AttackModule.get_markup_description(item.text)

        # region Navigation
        def go_to_selected_module_page(self):
            match self.selectedAttackModule:
                case AttackModule.SPECIFIC.value:
                    self.manager.current = ScreenNames.ATTACK_SPECIFIC_TECHNIQUE_PAGE.value
                    self.manager.transition.direction = "left"
                case AttackModule.CUSTOM.value:
                    self.manager.current = ScreenNames.CUSTOM_ATTACKS_PAGE.value
                    self.manager.transition.direction = "left"

                    self.app.update_attack_params_availability()
                case _:
                    self.app.show_dialog(Text.DIALOG_TITLE_NO_OPTION_SELECTED.value, Text.DIALOG_PROVIDE_OPTION.value)

        def go_back(self):
            self.manager.current = ScreenNames.HOME_PAGE.value
            self.manager.transition.direction = "right"
        # endregion


    class AttackSpecificTechniquePage(Screen):
        selectedTechnique = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for technique in StegoTechnique:
                tempWidget = OneLineListItem(text=f"{technique.value}", on_release=self.on_specific_technique_click)
                self.ids.specificTechniquesList.add_widget(tempWidget)

            del tempWidget

        def on_specific_technique_click(self, item: OneLineListItem):
            self.selectedTechnique = item.text
            self.ids.specificTechniqueInfo.text = StegoTechnique.get_markup_description(item.text)

        # region Navigation
        def go_to_attack_technique_page(self):
            match self.selectedTechnique:
                case StegoTechnique.LSB.value:
                    self.manager.current = ScreenNames.ATTACK_LSB_TECHNIQUE_PAGE.value
                    self.manager.transition.direction = "left"

                    self.app.update_attack_params_availability()
                case StegoTechnique.BPCS.value:
                    self.manager.current = ScreenNames.ATTACK_BPCS_TECHNIQUE_PAGE.value
                    self.manager.transition.direction = "left"

                    self.app.update_attack_params_availability()
                case StegoTechnique.METADATA.value:
                    self.manager.current = ScreenNames.ATTACK_METADATA_TECHNIQUE_PAGE.value
                    self.manager.transition.direction = "left"

                    self.app.update_attack_params_availability()
                case _:
                    self.app.show_dialog(Text.DIALOG_TITLE_NO_OPTION_SELECTED.value, Text.DIALOG_PROVIDE_OPTION.value)

        def go_back(self):
            self.manager.current = ScreenNames.CHOOSE_ATTACK_MODULE_PAGE.value
            self.manager.transition.direction = "right"
        # endregion


    class AttackLSBTechniquePage(Screen):
        analysisAttacks = [
            AttackOption.HISTOGRAM_ANALYSIS.value
        ]
        stegoFileAttacks = [
            AttackOption.LSB_DESTROY_ATTACK.value,
            AttackOption.LSB_EXTRACTION.value]
        selectedAttacks = []

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for attack in self.analysisAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            for attack in self.stegoFileAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            del tempWidget

        # region Navigation
        def go_back(self):
            self.manager.current = ScreenNames.ATTACK_SPECIFIC_TECHNIQUE_PAGE.value
            self.manager.transition.direction = "right"
        # endregion


    class AttackBPCSTechniquePage(Screen):
        analysisAttacks = [
            AttackOption.BIT_PLANES_COMPARE.value
        ]
        stegoFileAttacks = [
            AttackOption.BIT_PLANES_SPLIT.value,
            AttackOption.BIT_PLANES_OVERLAP.value
        ]

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for attack in self.analysisAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            for attack in self.stegoFileAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            del tempWidget

        def go_back(self):
            self.manager.current = ScreenNames.ATTACK_SPECIFIC_TECHNIQUE_PAGE.value
            self.manager.transition.direction = "right"


    class AttackMETADATATechniquePage(Screen):
        analysisAttacks = []
        stegoFileAttacks = [
            AttackOption.METADATA_DESTRUCTION.value,
            AttackOption.METADATA_EXTRACTION.value
        ]

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for attack in self.stegoFileAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            del tempWidget

        def go_back(self):
            self.manager.current = ScreenNames.ATTACK_SPECIFIC_TECHNIQUE_PAGE.value
            self.manager.transition.direction = "right"


    class CustomAttacksPage(Screen):
        analysisAttacks = [
            AttackOption.BIT_PLANES_COMPARE.value,
            AttackOption.HISTOGRAM_ANALYSIS.value,
        ]
        stegoFileAttacks = [
            AttackOption.BIT_PLANES_SPLIT.value,
            AttackOption.BIT_PLANES_OVERLAP.value,
            AttackOption.LSB_DESTROY_ATTACK.value,
            AttackOption.LSB_EXTRACTION.value,
            AttackOption.METADATA_DESTRUCTION.value,
            AttackOption.METADATA_EXTRACTION.value
        ]

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for attack in self.analysisAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)
                self.ids.attacksList.add_widget(tempWidget)

            for attack in self.stegoFileAttacks:
                tempWidget = self.app.init_checkbox_text_widget(attack)

                self.ids.attacksList.add_widget(tempWidget)

            del tempWidget

        def go_back(self):
            self.manager.current = ScreenNames.CHOOSE_ATTACK_MODULE_PAGE.value
            self.manager.transition.direction = "right"


    class ChooseEmbedOptionPage(Screen):
        selectedEmbedOption = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            for embed in EmbedOption:
                tempWidget = OneLineListItem(text=f"{embed.value}", on_release=self.on_specific_embed_option_click)
                self.ids.embedOptionsList.add_widget(tempWidget)

            del tempWidget

        def on_specific_embed_option_click(self, item: OneLineListItem):
            self.selectedEmbedOption = item.text
            self.ids.embedOptionInfo.text = EmbedOption.get_markup_description(item.text)

        # region Navigation
        def go_to_embed_option_page(self):
            self.manager: WindowManager
            match self.selectedEmbedOption:
                case EmbedOption.LSB.value:
                    self.manager.current = ScreenNames.EMBED_LSB_PAGE.value
                    self.manager.transition.direction = "left"
                case EmbedOption.METADATA.value:
                    self.manager.current = ScreenNames.EMBED_METADATA_PAGE.value
                    self.manager.transition.direction = "left"
                case _:
                    self.app.show_dialog(Text.DIALOG_TITLE_NO_OPTION_SELECTED.value, Text.DIALOG_PROVIDE_OPTION.value)

        def go_back(self):
            self.manager.current = ScreenNames.HOME_PAGE.value
            self.manager.transition.direction = "right"
        # endregion


    class EmbedLSBPage(Screen):
        method = EmbedOption.LSB.value
        params = {
            method: {},
        }

        file_path = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            self.embedParamsContainer: GridLayout = self.ids.embedParamsContainer

            param = LSBHandlerParams.EMBED_OPTION.value
            input_widget = self.app.init_dropdown_input_widget(
                bounding_class=self,
                method=self.method,
                param=param,
                available_values=[e.value for e in LSBEmbedPixelOption],
                multiselect=False
            )
            self.embedParamsContainer.add_widget(input_widget)

            param = LSBHandlerParams.COLORS_TO_USE.value
            input_widget = self.app.init_dropdown_input_widget(
                bounding_class=self,
                method=self.method,
                param=param,
                available_values=[e.value for e in ColorType]
            )
            self.embedParamsContainer.add_widget(input_widget)

            param = LSBHandlerParams.PERCENTAGE_TO_COVER.value
            input_widget = self.app.init_text_input_widget(
                bounding_class=self,
                method=self.method,
                param=param,
                hints=['range: [0,1]'],
                multiline=False,
            )
            self.embedParamsContainer.add_widget(input_widget)

            param = LSBHandlerParams.MESSAGE_TO_HIDE.value
            input_widget = self.app.init_text_input_widget(
                bounding_class=self,
                method=self.method,
                param=param,
                multiline=True,
            )
            self.embedParamsContainer.add_widget(input_widget)

        # region Embed init
        def perform_embed_options(self):
            lsb_handler = LSBHandler(
                self.app.base_folder,
                self.file_path
            )

            colors_to_embed = self.app.get_string_values_from_input(
                self.params[self.method][LSBHandlerParams.COLORS_TO_USE.value]
            )

            percentage_widget: Widget = self.params[self.method][LSBHandlerParams.PERCENTAGE_TO_COVER.value]
            if percentage_widget.text == '' or percentage_widget.text == Text.EMPTY_FILE.value:
                wanted_percentage = None
            else:
                wanted_percentage = float(percentage_widget.text)

            embed_option = self.app.get_string_value_from_input(
                self.params[self.method][LSBHandlerParams.EMBED_OPTION.value]
            )

            message = self.app.get_string_value_from_input(
                self.params[self.method][LSBHandlerParams.MESSAGE_TO_HIDE.value]
            )

            lsb_handler.hide_message(
                message=message,
                embed_option=embed_option,
                wanted_percentage=wanted_percentage,
                colors_to_embed=colors_to_embed
            )
        # endregion

        # region Navigation
        def go_back(self):
            self.manager.current = ScreenNames.CHOOSE_EMBED_OPTION_PAGE.value
            self.manager.transition.direction = "right"

        def go_to_embedding_loading(self):
            if not self.file_path or self.file_path == Text.EMPTY_FILE.value:
                self.app.show_dialog(
                    title="No file provided",
                    text="Please provide the file."
                )
                return

            manager: WindowManager = self.manager
            loading_page = manager.get_screen(ScreenNames.EMBEDDING_LOADING_PAGE.value)
            loading_page.executor = self

            self.manager.current = ScreenNames.EMBEDDING_LOADING_PAGE.value
            self.manager.transition.direction = "left"
        # endregion

        # region Helpers
        def select_file(self, screen):
            tk.withdraw()

            path = filedialog.askopenfilename()
            Window.raise_window()

            head, tail = os.path.split(path)
            if tail == "":
                tail = Text.EMPTY_FILE.value
                self.file_path = None
            else:
                self.file_path = path

            screen.ids.selectedFileName.text = tail
        # endregion


    class EmbedMETADATAPage(Screen):
        method = EmbedOption.METADATA.value
        params = {
            method: {},
        }

        file_path = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()
            self.__init_widgets()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def __init_widgets(self):
            self.embedParamsContainer: GridLayout = self.ids.embedParamsContainer

            desc_label = self.app.init_description_widget(
                text=Text.METADATA_TAGS_NOTE_EMBEDDING_DESCRIPTION.value
            )
            desc_label.on_ref_press = lambda x: self.open_site(url=x)
            self.embedParamsContainer.add_widget(desc_label)

            tags_input = self.app.init_text_input_widget(
                bounding_class=self,
                method=self.method,
                param=MetadataHandlerParams.METADATA_KEY.value,
                multiline=True,
            )
            self.embedParamsContainer.add_widget(tags_input)

        # region Embed init
        def perform_embed_options(self):
            ma = MetadataHandler(
                folder=self.app.base_folder,
                src=self.file_path,
            )

            tagsInput = self.params[self.method][MetadataHandlerParams.METADATA_KEY.value]
            tagsDict = self.app.get_tag_keys_values_from_input(
                tagsInput
            )

            ma.alter_tags(tagsDict)
        # endregion

        # region Navigation
        def go_back(self):
            self.manager.current = ScreenNames.CHOOSE_EMBED_OPTION_PAGE.value
            self.manager.transition.direction = "right"

        def go_to_embedding_loading(self):
            if not self.file_path or self.file_path == Text.EMPTY_FILE.value:
                self.app.show_dialog(
                    title="No file provided",
                    text="Please provide the file."
                )
                return

            manager: WindowManager = self.manager
            loading_page = manager.get_screen(ScreenNames.EMBEDDING_LOADING_PAGE.value)
            loading_page.executor = self

            self.manager.current = ScreenNames.EMBEDDING_LOADING_PAGE.value
            self.manager.transition.direction = "left"
        # endregion

        # region Helpers
        def select_file(self, screen):
            tk.withdraw()

            path = filedialog.askopenfilename()
            Window.raise_window()

            head, tail = os.path.split(path)
            if tail == "":
                tail = Text.EMPTY_FILE.value
                self.file_path = None
            else:
                self.file_path = path

            screen.ids.selectedFileName.text = tail
        # endregion


    class EmbeddingLoadingPage(Screen):
        executor: EmbedLSBPage | EmbedMETADATAPage | None = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        def on_enter(self, *args):
            if self.executor:
                self.executor.perform_embed_options()

                self.manager.current = ScreenNames.EMBEDDING_RESULTS_PAGE.value
                self.manager.transition.direction = "left"
            else:
                self.manager.current = ScreenNames.EMBEDDING_ERROR_PAGE.value
                self.manager.transition.direction = "left"


    class EmbeddingResultsPage(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()


    class CustomizeSelectedAttacksPage(Screen):
        params = {
            AttackOption.BIT_PLANES_COMPARE.value: {},
            AttackOption.BIT_PLANES_SPLIT.value: {},
            AttackOption.BIT_PLANES_OVERLAP.value: {},

            AttackOption.LSB_DESTROY_ATTACK.value: {},
            AttackOption.LSB_EXTRACTION.value: {},
            AttackOption.HISTOGRAM_ANALYSIS.value: {},

            AttackOption.METADATA_EXTRACTION.value: {},
            AttackOption.METADATA_DESTRUCTION.value: {}
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

            self.attackOptionsContainer: GridLayout = self.ids.attackOptionsContainer

        def on_enter(self, *args):
            self.app.attacks = {}

        # region Init widgets
        def clear_attack_widgets(self):
            self.attackOptionsContainer.clear_widgets()

        def init_widgets(self):
            for attack in self.app.selectedAttacks:
                match attack:
                    case AttackOption.BIT_PLANES_COMPARE.value:
                        self.__setup_BPCS_handler_widgets(
                            attack,
                            [BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value, BPCSAnalyzerParams.COLOR_CHANNELS.value]
                        )

                    case AttackOption.BIT_PLANES_OVERLAP.value:
                        self.__setup_BPCS_handler_widgets(
                            attack,
                            [BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value]
                        )

                    case AttackOption.BIT_PLANES_SPLIT.value:
                        self.__setup_BPCS_handler_widgets(
                            attack,
                            [BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value, BPCSAnalyzerParams.COLOR_CHANNELS.value]
                        )

                    case AttackOption.LSB_DESTROY_ATTACK.value:
                        self.__setup_LSB_analyzer_widgets(attack)

                    case AttackOption.LSB_EXTRACTION.value:
                        self.__setup_LSB_analyzer_widgets(attack)

                    case AttackOption.HISTOGRAM_ANALYSIS.value:
                        pass
                    case AttackOption.METADATA_EXTRACTION.value:
                        self.__setup_METADATA_widgets(attack)
                    case AttackOption.METADATA_DESTRUCTION.value:
                        pass
                    case _:
                        raise Exception("Invalid method selected.")

        def __setup_METADATA_widgets(self, attack):
            container = self.attackOptionsContainer

            title = self.app.init_subtitle_widget(
                text=attack,
            )
            container.add_widget(title)

            desc_label = self.app.init_description_widget(
                text=Text.METADATA_TAGS_NOTE_EXTRACTION_DESCRIPTION.value
            )
            desc_label.on_ref_press = lambda x: self.open_site(url=x)
            container.add_widget(desc_label)

            input_widget = self.app.init_text_input_widget(
                bounding_class=self,
                method=attack,
                param=MetadataHandlerParams.METADATA_KEY.value,
            )
            container.add_widget(input_widget)

        def __setup_BPCS_handler_widgets(self, attack, params):
            container = self.attackOptionsContainer

            title = self.app.init_subtitle_widget(
                text=attack,
            )
            container.add_widget(title)

            for param in params:
                match param:
                    case BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value:
                        input_widget = self.app.init_dropdown_input_widget(
                                    bounding_class=self,
                                    method=attack,
                                    param=param,
                                    available_values=[i+1 for i in range(8)]
                                )
                        container.add_widget(input_widget)

                    case BPCSAnalyzerParams.COLOR_CHANNELS.value:
                        input_widget = self.app.init_dropdown_input_widget(
                                    bounding_class=self,
                                    method=attack,
                                    param=param,
                                    available_values=[e.value for e in ColorType]
                                )
                        container.add_widget(input_widget)

                    case _:
                        raise Exception("Invalid param for BPCS.")

        def __setup_LSB_analyzer_widgets(self, attack):
            container = self.attackOptionsContainer

            title = self.app.init_subtitle_widget(
                text=attack,
            )
            container.add_widget(title)

            param = LSBHandlerParams.EMBED_OPTION.value
            input_widget = self.app.init_dropdown_input_widget(
                bounding_class=self,
                method=attack,
                param=param,
                available_values=[e.value for e in LSBEmbedPixelOption],
                multiselect=False
            )
            container.add_widget(input_widget)

            param = LSBHandlerParams.COLORS_TO_USE.value
            input_widget = self.app.init_dropdown_input_widget(
                bounding_class=self,
                method=attack,
                param=param,
                available_values=[e.value for e in ColorType]
            )
            container.add_widget(input_widget)

            param = LSBHandlerParams.PERCENTAGE_TO_COVER.value
            input_widget = self.app.init_text_input_widget(
                bounding_class=self,
                method=attack,
                param=param,
                hints=['range: [0,1]'],
                multiline=False,
            )
            container.add_widget(input_widget)
        # endregion

        # region Navigation
        def go_back(self):
            self.manager.current = self.app.lastActiveScreen
            self.manager.transition.direction = "right"

        def go_to_attacks_loading_page(self):
            self.manager.current = ScreenNames.ATTACKS_LOADING_PAGE.value
            self.manager.transition.direction = "left"
        # endregion

        # region Init selected attacks
        def init_attacks(self):
            for attack in self.app.selectedAttacks:
                match attack:
                    case AttackOption.BIT_PLANES_COMPARE.value:
                        bit_plane_analyzer = BitPlaneAnalyzer(
                            self.app.base_folder,
                            self.app.stegoFilePath,
                            self.app.originalFilePath
                        )

                        bit_planes_to_keep = self.app.get_int_values_from_input(
                            self.params[attack][BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value]
                        )

                        color_channels = self.app.get_string_values_from_input(
                            self.params[attack][BPCSAnalyzerParams.COLOR_CHANNELS.value]
                        )

                        p1 = multiprocessing.Process(
                            target=bit_plane_analyzer.separate_channels(
                                file_origin_type=FileOriginType.ORIGINAL.value,
                                bit_planes_to_split=bit_planes_to_keep,
                                color_channels=color_channels
                            ))
                        p1.start()

                        p2 = multiprocessing.Process(
                            target=bit_plane_analyzer.separate_channels(
                                file_origin_type=FileOriginType.STEGO.value,
                                bit_planes_to_split=bit_planes_to_keep,
                                color_channels=color_channels
                            ))
                        p2.start()

                        self.app.attacks[attack] = ToolProcesses(tool=bit_plane_analyzer, processes=[p1, p2])

                    case AttackOption.BIT_PLANES_OVERLAP.value:
                        bit_plane_analyzer = BitPlaneAnalyzer(
                            self.app.base_folder,
                            self.app.stegoFilePath,
                            self.app.originalFilePath
                        )

                        bit_planes_to_keep = self.app.get_int_values_from_input(
                            self.params[attack][BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value]
                        )

                        p = multiprocessing.Process(
                            target=bit_plane_analyzer.overlap_bit_planes(
                                file_origin_type=FileOriginType.STEGO.value,
                                bit_planes_to_overlap=bit_planes_to_keep
                            ))
                        self.app.attacks[attack] = ToolProcesses(tool=bit_plane_analyzer, processes=[p])
                        p.start()

                    case AttackOption.BIT_PLANES_SPLIT.value:
                        bit_plane_analyzer = BitPlaneAnalyzer(
                            self.app.base_folder,
                            self.app.stegoFilePath,
                            self.app.originalFilePath
                        )

                        bit_planes_to_keep = self.app.get_int_values_from_input(
                            self.params[attack][BPCSAnalyzerParams.BIT_PLANES_TO_KEEP.value]
                        )

                        color_channels = self.app.get_string_values_from_input(
                            self.params[attack][BPCSAnalyzerParams.COLOR_CHANNELS.value]
                        )

                        p = multiprocessing.Process(
                            target=bit_plane_analyzer.separate_channels(
                                file_origin_type=FileOriginType.STEGO.value,
                                bit_planes_to_split=bit_planes_to_keep,
                                color_channels=color_channels
                            ))
                        self.app.attacks[attack] = ToolProcesses(tool=bit_plane_analyzer, processes=[p])
                        p.start()

                    case AttackOption.LSB_DESTROY_ATTACK.value:
                        lsb_handler = LSBHandler(
                            self.app.base_folder,
                            self.app.stegoFilePath
                        )

                        colors_to_embed = self.app.get_string_values_from_input(
                            self.params[attack][LSBHandlerParams.COLORS_TO_USE.value]
                        )

                        percentage_widget: Widget = self.params[attack][LSBHandlerParams.PERCENTAGE_TO_COVER.value]
                        if percentage_widget.text == '' or percentage_widget.text == Text.EMPTY_FILE.value:
                            percentage = None
                        else:
                            percentage = float(percentage_widget.text)

                        embed_option = self.app.get_string_value_from_input(
                            self.params[attack][LSBHandlerParams.EMBED_OPTION.value]
                        )

                        p = multiprocessing.Process(
                            target=lsb_handler.destroy_message(
                                embed_option=embed_option,
                                colors_to_embed=colors_to_embed,
                                destroy_percentage=percentage
                            ))
                        self.app.attacks[attack] = ToolProcesses(tool=lsb_handler, processes=[p])
                        p.start()

                    case AttackOption.LSB_EXTRACTION.value:
                        lsb_handler = LSBHandler(
                            self.app.base_folder,
                            self.app.stegoFilePath
                        )

                        colors_to_embed = self.app.get_string_values_from_input(
                            self.params[attack][LSBHandlerParams.COLORS_TO_USE.value]
                        )

                        percentage_widget: Widget = self.params[attack][LSBHandlerParams.PERCENTAGE_TO_COVER.value]
                        if percentage_widget.text == '' or percentage_widget.text == Text.EMPTY_FILE.value:
                            percentage = None
                        else:
                            percentage = float(percentage_widget.text)

                        embed_option = self.app.get_string_value_from_input(
                            self.params[attack][LSBHandlerParams.EMBED_OPTION.value]
                        )

                        p = multiprocessing.Process(
                            target=lsb_handler.extract_message(
                                embed_option=embed_option,
                                colors_to_read=colors_to_embed,
                                percentage=percentage
                            ))
                        self.app.attacks[attack] = ToolProcesses(tool=lsb_handler, processes=[p])
                        p.start()

                    case AttackOption.HISTOGRAM_ANALYSIS.value:
                        histogram_analyzer = HistogramAnalyzer(
                            folder=self.app.base_folder,
                            stegoImgSrc=self.app.stegoFilePath,
                            originalImgSrc=self.app.originalFilePath
                        )

                        p = multiprocessing.Process(target=histogram_analyzer.analyze())
                        self.app.attacks[attack] = ToolProcesses(tool=histogram_analyzer, processes=[p])
                        p.start()

                    case AttackOption.METADATA_EXTRACTION.value:
                        metadata_analyzer = MetadataHandler(
                            folder=self.app.base_folder,
                            src=self.app.stegoFilePath
                        )

                        tagKeys = self.app.get_tag_keys_from_input(
                            self.params[attack][MetadataHandlerParams.METADATA_KEY.value]
                        )

                        p = multiprocessing.Process(target=metadata_analyzer.read_tags(keys_to_read=tagKeys))
                        self.app.attacks[attack] = ToolProcesses(tool=metadata_analyzer, processes=[p])
                        p.start()

                    case AttackOption.METADATA_DESTRUCTION.value:
                        metadata_analyzer = MetadataHandler(
                            folder=self.app.base_folder,
                            src=self.app.stegoFilePath
                        )

                        p = multiprocessing.Process(target=metadata_analyzer.scramble_tags())
                        self.app.attacks[attack] = ToolProcesses(tool=metadata_analyzer, processes=[p])
                        p.start()

        def start_processes(self):
            for attackKey in self.app.attacks:
                wrapper: ToolProcesses = self.app.attacks[attackKey]
                for process in wrapper.processes:
                    process.join()
        # endregion

        # region Helpers
        def open_site(self, url):
            webbrowser.open(url)
        # endregion


    class EmbeddingErrorPage(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()


    class AttacksLoadingPage(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def on_enter(self, *args):
            customize_attacks_page: CustomizeSelectedAttacksPage =\
                self.manager.get_screen(ScreenNames.CUSTOMIZE_SELECTED_ATTACKS_PAGE.value)
            customize_attacks_page.init_attacks()
            customize_attacks_page.start_processes()

            attack_results_page: AttacksResultsPage = self.manager.get_screen(ScreenNames.ATTACKS_RESULTS_PAGE.value)
            attack_results_page.init_widgets()

            self.go_to_attacks_results()

        def __init_vars(self):
            self.app: ExStegoApp = MDApp.get_running_app()

        def go_to_attacks_results(self):
            self.manager.current = ScreenNames.ATTACKS_RESULTS_PAGE.value
            self.manager.transition.direction = "left"


    class AttacksResultsPage(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def on_kv_post(self, base_widget):
            self.__init_vars()

        def __init_vars(self):
            self.manager: WindowManager
            self.app: ExStegoApp = MDApp.get_running_app()

        # region Results init
        def init_widgets(self):
            results_container: MDGridLayout = self.ids.resultsContainer

            description = MDLabel(
                markup=True,
                text=f"[color=3D3D3D]"
                     f"For logs and standalone results visit folder: ./{self.app.base_folder}"
                     f"[/color]",
                halign="center",
                valign="center",
            )
            self.ids.title.add_widget(description)

            for attackKey in self.app.attacks:
                wrapper: ToolProcesses = self.app.attacks[attackKey]
                results: any = wrapper.tool.results
                result_type = type(results)

                title = MDLabel(
                    size_hint_y=None,
                    size_hint_x=1,
                    markup=True,
                    height=100,
                    halign="center",
                    valign="center",
                    text=f"[size={self.app.title2_size}dp]{attackKey}[/size]"
                )
                results_container.add_widget(title)

                if result_type is MetadataHandlerResults:
                    results: MetadataHandlerResults

                    match attackKey:
                        case AttackOption.METADATA_DESTRUCTION.value:
                            tags_title = self.__init_label_widget(
                                title="Destroyed tags: "
                            )

                            tags_origin_titles = self.__init_horizontal_text_widget(
                                results=[
                                    "Original tags",
                                    "Destroyed tags"
                                ]
                            )

                            o_tags = ''
                            d_tags = ''
                            for key in results.original_tags:
                                o_tags += results.original_tags[key]
                            for key in results.destroyed_tags:
                                d_tags += results.destroyed_tags[key]

                            tags_container = self.__init_horizontal_text_widget(
                                results=[o_tags, d_tags],
                                halign="left",
                                valign="top"
                            )

                            results_container.add_widget(tags_title)
                            results_container.add_widget(tags_origin_titles)
                            results_container.add_widget(tags_container)

                        case AttackOption.METADATA_EXTRACTION.value:
                            tags_title = self.__init_label_widget(
                                title="Tags: "
                            )

                            tags = ''
                            for key in results.original_tags:
                                tags += results.original_tags[key]
                            tags_container = self.__init_horizontal_text_widget(
                                results=[tags],
                                halign="left",
                            )

                            results_container.add_widget(tags_title)
                            results_container.add_widget(tags_container)

                elif result_type is HistogramAnalyzerResults:
                    results: HistogramAnalyzerResults

                    histogram_percentage = self.__init_label_widget(
                        title=f"Equality percentage",
                        result=f"{results.equality_percentage*100}%"
                    )

                    histogram_title = self.__init_label_widget(
                        title=f"Histograms: ",
                    )

                    histogram_origin_titles = self.__init_horizontal_text_widget(
                        results=[f"{key}" for key in results.histogram_src]
                    )

                    histograms_container = self.__init_horizontal_image_widget(
                        height=250,
                        image_srcs=[f"{results.histogram_src[key]}" for key in results.histogram_src]
                    )

                    results_container.add_widget(histogram_percentage)
                    results_container.add_widget(histogram_title)
                    results_container.add_widget(histogram_origin_titles)
                    results_container.add_widget(histograms_container)

                elif result_type is LSBHandlerResults:
                    results: LSBHandlerResults
                    match attackKey:
                        case AttackOption.LSB_DESTROY_ATTACK.value:
                            success_message = self.__init_label_widget(
                                title="Data destroyed."
                                      " Try to extract using the same embedding program."
                            )

                            results_container.add_widget(success_message)

                        case AttackOption.LSB_EXTRACTION.value:
                            messages_title = self.__init_label_widget(
                                title="Data: "
                            )

                            height = 0
                            for line in results.extracted_text.splitlines():
                                height += 4.2
                            message_container = self.__init_horizontal_text_widget(
                                results=[
                                    results.extracted_text
                                ],
                                halign="left"
                            )

                            results_container.add_widget(messages_title)
                            results_container.add_widget(message_container)

                elif result_type is BPCSAnalyzerResults:
                    results: BPCSAnalyzerResults
                    match attackKey:
                        case AttackOption.BIT_PLANES_SPLIT.value:
                            o_planes = results.bit_planes_per_channel[FileOriginType.STEGO.value]
                            planes_no = 0
                            used_color_keys = []
                            for color_key in o_planes:
                                if o_planes[color_key]:
                                    used_color_keys.append(color_key)
                                    if len(o_planes[color_key]) > planes_no:
                                        planes_no = len(o_planes[color_key])

                            for color_key in used_color_keys:
                                color_title = self.__init_label_widget(
                                    title=f"{str.capitalize(color_key)}: "
                                )
                                images_container = self.__init_scroll_images_y_widget(
                                    max_item_width=300,
                                    max_item_height=300,
                                    cols=planes_no,
                                    titles=[f"Plane {i+1}" for i in range(planes_no)],
                                    image_srcs=o_planes[color_key]
                                )

                                results_container.add_widget(color_title)
                                results_container.add_widget(images_container)

                        case AttackOption.BIT_PLANES_OVERLAP.value:
                            title = self.__init_label_widget(
                                title=f"Planes overlap: ",
                            )

                            overlap_image_container = self.__init_horizontal_image_widget(
                                height=300,
                                image_srcs=[results.planes_overlap_image[FileOriginType.STEGO.value]]
                            )

                            results_container.add_widget(title)
                            results_container.add_widget(overlap_image_container)

                        case AttackOption.BIT_PLANES_COMPARE.value:
                            planes = results.bit_planes_per_channel

                            o_planes = results.bit_planes_per_channel[FileOriginType.STEGO.value]
                            planes_no = 0
                            used_color_keys = []
                            for color_key in o_planes:
                                if o_planes[color_key]:
                                    used_color_keys.append(color_key)
                                    if len(o_planes[color_key]) > planes_no:
                                        planes_no = len(o_planes[color_key])

                            for color_key in used_color_keys:
                                for e in FileOriginType:
                                    color_title = self.__init_label_widget(
                                        title=f"[{e.value}] {str.capitalize(color_key)}: "
                                    )
                                    images_container = self.__init_scroll_images_y_widget(
                                        max_item_width=300,
                                        max_item_height=300,
                                        cols=planes_no,
                                        titles=[f"Plane {i + 1}" for i in range(planes_no)],
                                        image_srcs=planes[e.value][color_key]
                                    )

                                    results_container.add_widget(color_title)
                                    results_container.add_widget(images_container)
        # endregion

        # region Widget init
        def __init_label_widget(self, title, result=None):
            height = 50

            if result is None:
                message = title
            else:
                message = f"{title}: {result}"
            label = MDLabel(
                size_hint_y=None,
                size_hint_x=1,
                height=height,
                halign="left",
                valign="center",
                text=message
            )

            return label

        def __init_horizontal_text_widget(self,
                                          results,
                                          halign="center",
                                          valign="top",
                                          ):
            base_height = 100
            container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                minimum_height=dp(base_height),
            )
            for result in results:
                widget = MDLabel(
                        size_hint_y=None,
                        halign=halign,
                        valign=valign,
                        height=dp(base_height),
                        text=result
                    )
                widget.bind(
                    texture_size=lambda x, y: {
                        self.app.set_child_parent_widget_height(x, y[1])
                    }
                )
                container.add_widget(widget)

            return container

        def __init_horizontal_image_widget(self, height, image_srcs):
            container = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                size_hint_x=1,
                height=dp(height),
            )
            for src in image_srcs:
                container.add_widget(
                    Image(
                        source=src,
                        keep_ratio=True
                    ))

            return container

        def __init_scroll_images_y_widget(self,
                                          max_item_width,
                                          max_item_height,
                                          cols,
                                          image_srcs,
                                          titles,
                                          ):
            title_height = 50
            spacing = 20

            if len(titles) < len(image_srcs):
                additional_titles = len(image_srcs) - len(titles)
                for i in range(additional_titles):
                    titles.append("")

            total_height = title_height + max_item_height
            total_width = (max_item_width+20)*cols
            h_scroll = HorizontalScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                size_hint_y=None,
                height=total_height,
            )

            container = GridLayout(
                spacing=spacing,
                cols=cols,
                size_hint_y=1,
                size_hint_x=None,
                width=total_width,
            )

            for title in titles:
                container.add_widget(
                    MDLabel(
                        size_hint_y=None,
                        size_hint_x=None,
                        width=max_item_width,
                        height=title_height,
                        text_size=container.size,
                        halign="center",
                        valign="center",
                        text=title
                    )
                )
            for src in image_srcs:
                container.add_widget(
                    Image(
                        source=src,
                        keep_ratio=True,
                        size_hint=(None, None),
                        height=max_item_height,
                        width=max_item_width,
                    )
                )

            h_scroll.add_widget(container)

            return h_scroll
        # endregion
    # endregion

    # region App
    class ExStegoApp(MDApp):
        # region Sizes
        main_title_size = dp(44)
        title1_size = dp(34)
        title2_size = dp(24)

        icon_large_size = dp(60)
        icon_medium_size = dp(45)

        description_line_height = 1.25

        input_height = 80
        result_text_height = 50
        # endregion

        # region Colors
        black_color = rgba("#000000")
        white_color = rgba("#FFFFFF")
        transparent_color = (0, 0, 0, 0)

        blue_crayola_color = rgba("#478BC2")

        sea_green_color = rgba("#0EBE78")

        alabaster_color = rgba("#F1F2EB")
        timberwolf_color = rgba("#D8DAD3")

        imperial_red_color = rgba("#F0052C")

        onyx_color = rgba("#3D3D3D")
        # endregion

        base_folder = None

        attacks = {}

        analysisAttacks = []
        stegoFileAttacks = []

        selectedAttacks = []

        stegoFilePath = None
        originalFilePath = None

        areAnalysisAttacksAvailable = False
        areStegoFileAttacksAvailable = False

        dialog = None

        lastActiveScreen: Screen = None

        # region Init
        def __init__(self):
            super(ExStegoApp, self).__init__()
            self.__init_variables()

        def build(self):
            self.theme_cls.theme_style = "Dark"
            self.root = Builder.load_file("ui/Exstego.kv")

        def __setup_folder_name(self):
            today = date.today()
            time = today.strftime("%b_%d_%Y")
            self.base_folder = 'RESULTS' + '/' + time + '__' + shortuuid.ShortUUID().uuid().title()

            MessageHelper.src = self.base_folder
            # NOTE
            # logger can be disabled
            # MessageHelper.to_print = False
            # if the app is run using a environment supporting termcolor library (like PyCharm), set to True
            MessageHelper.is_colored_logger = True

        def __init_variables(self):
            self.__setup_folder_name()
        # endregion

        # region Navigation
        def go_to_choose_attack_module_page(self):
            self.root.current = ScreenNames.CHOOSE_ATTACK_MODULE_PAGE.value
            self.root.transition.direction = "left"

        def go_to_choose_embed_option_page(self):
            self.root.current = ScreenNames.CHOOSE_EMBED_OPTION_PAGE.value
            self.root.transition.direction = "left"

        def go_to_customize_attacks_page(self, screenName):
            screen: CustomizeSelectedAttacksPage = self.root.get_screen(
                ScreenNames.CUSTOMIZE_SELECTED_ATTACKS_PAGE.value
            )
            screen.clear_attack_widgets()
            screen.init_widgets()

            attackOptionsContainer: Widget = screen.ids.attackOptionsContainer
            if len(attackOptionsContainer.children) == 0:
                screen.go_to_attacks_loading_page()
            else:
                self.lastActiveScreen = screenName
                self.root.current = ScreenNames.CUSTOMIZE_SELECTED_ATTACKS_PAGE.value
                self.root.transition.direction = "left"

        def go_to_init_embedding_page(self):
            pass
        # endregion

        # region Data & attacks selection handling
        def __reset_available_data_params(self, activeScreen: Screen):
            self.areAnalysisAttacksAvailable = False
            self.areStegoFileAttacksAvailable = False
            self.stegoFilePath = None
            self.originalFilePath = None

            self.activeScreen = activeScreen
            if 'selectedOriginalFileName' in activeScreen.ids:
                activeScreen.ids.selectedOriginalFileName.text = Text.EMPTY_FILE.value
            if 'selectedStegoFileName' in activeScreen.ids:
                activeScreen.ids.selectedStegoFileName.text = Text.EMPTY_FILE.value

        def update_attack_params_availability(self):
            match self.root.current:
                case ScreenNames.ATTACK_METADATA_TECHNIQUE_PAGE.value:
                    self.stegoFileAttacks = AttackMETADATATechniquePage.stegoFileAttacks
                    self.analysisAttacks = AttackMETADATATechniquePage.analysisAttacks
                    self.__reset_available_data_params(self.root.ids.attackMETADATATechniquePage)
                case ScreenNames.ATTACK_BPCS_TECHNIQUE_PAGE.value:
                    self.stegoFileAttacks = AttackBPCSTechniquePage.stegoFileAttacks
                    self.analysisAttacks = AttackBPCSTechniquePage.analysisAttacks
                    self.__reset_available_data_params(self.root.ids.attackBPCSTechniquePage)
                case ScreenNames.ATTACK_LSB_TECHNIQUE_PAGE.value:
                    self.stegoFileAttacks = AttackLSBTechniquePage.stegoFileAttacks
                    self.analysisAttacks = AttackLSBTechniquePage.analysisAttacks
                    self.__reset_available_data_params(self.root.ids.attackLSBTechniquePage)
                case ScreenNames.CUSTOM_ATTACKS_PAGE.value:
                    self.stegoFileAttacks = CustomAttacksPage.stegoFileAttacks
                    self.analysisAttacks = CustomAttacksPage.analysisAttacks
                    self.__reset_available_data_params(self.root.ids.customAttacksPage)
                case _:
                    raise Exception("Invalid screen.")

            activeScreen = self.root.get_screen(self.root.current)
            self.__update_attack_types_availability()
            self.__reset_attack_selection(activeScreen)
            self.selectedAttacks = []

        def __update_attack_selection(self, button, active: bool | None = None):
            if active is not None:
                # manual
                if active:
                    button.icon = Selection.SELECTED.value
                    self.selectedAttacks.append(button.text)
                else:
                    button.icon = Selection.UNSELECTED.value
                    self.selectedAttacks.remove(button.text)
            else:
                # toggle
                if button.icon == Selection.SELECTED.value:
                    button.icon = Selection.UNSELECTED.value
                    self.selectedAttacks.remove(button.text)
                else:
                    button.icon = Selection.SELECTED.value
                    self.selectedAttacks.append(button.text)

        def __deselect_attack(self, attack, activeScreen: Screen):
            for child in activeScreen.ids.attacksList.children:
                if type(child) is MDRectangleFlatIconButton:
                    if child.text == attack:
                        self.__update_attack_selection(button=child, active=False)

        def __reset_attack_selection(self, activeScreen: Screen):
            self.selectedAttacksTemp = deepcopy(self.selectedAttacks)
            for attack in self.selectedAttacksTemp:
                if not self.areAnalysisAttacksAvailable and attack in self.analysisAttacks:
                    self.__deselect_attack(attack, activeScreen)
                elif not self.areStegoFileAttacksAvailable and attack in self.stegoFileAttacks:
                    self.__deselect_attack(attack, activeScreen)

            del self.selectedAttacksTemp

        def __update_attack_types_availability(self):
            if self.stegoFilePath is not None and self.stegoFilePath != "":
                self.areStegoFileAttacksAvailable = True
                if self.originalFilePath is not None and self.originalFilePath != "":
                    self.areAnalysisAttacksAvailable = True
                else:
                    self.areAnalysisAttacksAvailable = False
            else:
                self.areStegoFileAttacksAvailable = False
                self.areAnalysisAttacksAvailable = False

        def attempt_attack_selection(self, button, active: bool | None = None):
            if button.text in self.stegoFileAttacks:
                if self.areStegoFileAttacksAvailable:
                    self.__update_attack_selection(button, active)
                else:
                    self.show_dialog(
                        title=Text.DIALOG_TITLE_NOT_AVAILABLE.value,
                        text=Text.STEGO_FILE_ATTACKS_UNAVAILABLE.value)
            elif button.text in self.analysisAttacks:
                if self.areAnalysisAttacksAvailable:
                    self.__update_attack_selection(button, active)
                else:
                    self.show_dialog(
                        title=Text.DIALOG_TITLE_NOT_AVAILABLE.value,
                        text=Text.ANALYSIS_ATTACKS_UNAVAILABLE.value)

        def select_original_file(self, button, activeScreen: Screen):
            tk.withdraw()

            path = filedialog.askopenfilename()
            Window.raise_window()

            head, tail = os.path.split(path)
            if tail == "":
                tail = Text.EMPTY_FILE.value
                self.originalFilePath = None
            else:
                self.originalFilePath = path

            activeScreen.ids.selectedOriginalFileName.text = tail
            self.__update_attack_types_availability()

            if not self.areAnalysisAttacksAvailable or not self.areStegoFileAttacksAvailable:
                self.__reset_attack_selection(activeScreen)

            del head, tail, path

        def select_stego_file(self, button, activeScreen: Screen):
            tk.withdraw()

            path = filedialog.askopenfilename()
            Window.raise_window()

            head, tail = os.path.split(path)
            if tail == "":
                tail = Text.EMPTY_FILE.value
                self.stegoFilePath = None
            else:
                self.stegoFilePath = path

            activeScreen.ids.selectedStegoFileName.text = tail
            self.__update_attack_types_availability()

            if not self.areAnalysisAttacksAvailable or not self.areStegoFileAttacksAvailable:
                self.__reset_attack_selection(activeScreen)

            del head, tail, path
        # endregion

        # region Helpers
        def show_dialog(self, title: str, text: str):
            self.dialog = MDDialog(
                title=str(title),
                text=str(text),
                buttons=[
                    MDFlatButton(
                        text="Ok",
                        on_release=lambda obj: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

        def get_text(self, filename):
            file = open(filename, 'r')
            return ''.join([line for line in file])

        def set_child_parent_widget_height(self, child: Widget, height):
            child.height = height

            parent: MDBoxLayout = child.parent
            max_height = height
            for c in parent.children:
                if c.height > max_height:
                    max_height = c.height
            parent.height = max_height
        # endregion

        # region Input widgets
        def init_description_widget(self, text: str):
            height = 0
            for line in text.splitlines():
                height += 20

            label = MDLabel(
                text=text,
                markup=True,
                font_size=self.title2_size,
                height=height,
                size_hint_y=None,
                size_hint_x=1,
            )

            return label

        def init_subtitle_widget(self, text):

            widget = MDLabel(
                text=f"[color=F1F2EB][size={self.title2_size}dp]{text}[/size][/color]",
                markup=True,
                font_size=self.title2_size,
                height=60,
                size_hint_y=None,
                size_hint_x=1
            )

            return widget

        def init_checkbox_text_widget(self, text, func=None):
            if func is None:
                func = self.attempt_attack_selection

            widget = MDRectangleFlatIconButton(
                text=f"{text}",
                on_release=func,
                icon=Selection.UNSELECTED.value,
                icon_color=self.white_color,
                text_color=self.white_color,
                line_color=self.transparent_color
            )

            return widget

        def init_text_input_widget(self,
                                   bounding_class,
                                   method,
                                   param,
                                   hints=None,
                                   multiline=True):
            hints_text = ''
            if hints is not None:
                hints_text = f'{hints[0]}'
                for val in hints[1:]:
                    hints_text += f', {val}'
                text = f"{param} - {hints_text}"
            else:
                text = f"{param}"

            base_height = 70
            input_wrapper = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                minimum_height=dp(base_height),
                padding=[11, 0, 11, 0],
            )
            widget = MDTextField(
                size_hint_y=None,
                hint_text=text,
                mode="rectangle",
                height=dp(base_height),
                multiline=multiline,
            )
            widget.bind(
                height=lambda x, y: {
                    self.set_child_parent_widget_height(x, y)
                }
            )

            input_wrapper.add_widget(widget)

            bounding_class.params[method][param] = widget

            return input_wrapper

        def init_slider_input_widget(self,
                                     bounding_class,
                                     method,
                                     param,
                                     minimum,
                                     maximum,
                                     value,
                                     step):
            slider_wrapper = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=80
            )
            slider_title = MDLabel(
                size_hint=(1, 0.5),
                markup=True,
                text=f"{param}"
            )

            slider = MDSlider(
                min=minimum,
                value=value,
                step=step,
                max=maximum,
                hint=True,
                hint_text_color=self.timberwolf_color,
                color=self.timberwolf_color
            )

            slider_wrapper.add_widget(slider_title)
            slider_wrapper.add_widget(slider)

            bounding_class.params[method][param] = slider

            return slider_wrapper

        def init_dropdown_input_widget(self,
                                       bounding_class,
                                       method,
                                       param,
                                       available_values,
                                       multiselect=True):
            menu_items = []
            for value in available_values:
                if multiselect:
                    func = lambda x=value: self.__update_values(
                        bounding_class=bounding_class,
                        method=method,
                        param=param,
                        value=x
                    )
                else:
                    func = lambda x=value: self.__update_value(
                        bounding_class=bounding_class,
                        method=method,
                        param=param,
                        value=x
                    )
                value = f"{value}"
                menu_items.append(
                    {
                        "viewclass": "OneLineListItem",
                        "text": value,
                        "on_release": func
                    }
                )

            input_button = MDIconButton(
                icon="arrow-down-drop-circle-outline",
            )
            menu_len = len(menu_items)*50
            if menu_len > 250:
                menu_len = 250
            menu = MDDropdownMenu(
                caller=input_button,
                items=menu_items,
                width_mult=4,
                max_height=dp(menu_len)
            )
            input_button: MDIconButton
            input_button.on_release = menu.open

            input_wrapper = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=80,
            )
            input_title = MDLabel(
                size_hint=(1, 0.5),
                markup=True,
                text=f"{param}"
            )
            input_value_button_wrapper = MDBoxLayout(
                padding=[15, 0, 0, 0],
                size_hint=(1, 0.5),
                md_bg_color=self.onyx_color
            )
            input_value = MDLabel(
                size_hint=(0.8, 1),
                markup=True,
                shorten=True,
                text=Text.EMPTY_VALUE.value
            )
            input_button_wrapper = AnchorLayout(
                size_hint=(0.2, 1),
                anchor_x="right"
            )

            input_button_wrapper.add_widget(input_button)
            input_value_button_wrapper.add_widget(input_value)
            input_value_button_wrapper.add_widget(input_button_wrapper)

            input_wrapper.add_widget(input_title)
            input_wrapper.add_widget(input_value_button_wrapper)

            bounding_class.params[method][param] = input_value

            return input_wrapper
        # endregion

        # region Inputs update
        def __update_value(self, bounding_class, method, param, value):

            value = str(value)
            input_widget: MDLabel = bounding_class.params[method][param]
            input_value: str = input_widget.text.strip()

            if input_value == Text.EMPTY_VALUE.value:
                input_widget.text = value
            else:
                if value == input_value:
                    input_value = input_value.replace(value, '')
                    input_value = input_value.strip()
                else:
                    input_value = value
                if input_value == '':
                    input_value = Text.EMPTY_VALUE.value

                input_widget.text = input_value

        def __update_values(self, bounding_class, method, param, value):
            value = str(value)
            input_widget: MDLabel = bounding_class.params[method][param]
            input_values: str = input_widget.text

            if input_values == Text.EMPTY_VALUE.value:
                input_widget.text = value
            else:
                input_values = input_values.strip()
                input_values = input_values.strip(',')
                if value in input_values:
                    input_values = input_values.replace(f' {value},', '')
                    input_values = input_values.replace(f'{value}, ', '')
                    input_values = input_values.replace(value, '')
                    input_values = input_values.rstrip()
                    input_values = input_values.lstrip()
                    input_values = input_values.rstrip(',')
                    input_values = input_values.lstrip(',')
                else:
                    input_values = input_values + f", {value}"
                if input_values == '':
                    input_values = Text.EMPTY_VALUE.value

                input_widget.text = input_values

        def get_int_values_from_input(self, input_widget: MDLabel):
            if input_widget.text == Text.EMPTY_VALUE.value:
                return None

            ints = []
            for value in input_widget.text.split(','):
                value = value.strip()
                ints.append(int(value))

            return ints

        def get_string_value_from_input(self, input_widget: MDLabel):
            if input_widget.text == Text.EMPTY_VALUE.value:
                return None

            string = input_widget.text
            string = string.strip()

            return string

        def get_string_values_from_input(self, input_widget: MDLabel | MDTextField):
            if input_widget.text == Text.EMPTY_VALUE.value:
                return None

            strings = []
            for value in input_widget.text.split(','):
                value = value.strip()
                strings.append(value)

            return strings

        def get_tag_keys_from_input(self, input_widget: MDTextField):
            if input_widget.text == Text.EMPTY_VALUE.value:
                return None

            tags = []
            for line in input_widget.text.splitlines():
                tags.append(line.strip())

            return tags

        def get_tag_keys_values_from_input(self, input_widget: MDTextField):
            if input_widget.text == Text.EMPTY_VALUE.value:
                return None

            tags_values = {}
            for line in input_widget.text.splitlines():
                line = line.strip()
                parts = line.split(':')
                tags_values[parts[0]] = parts[1]

            return tags_values
        # endregion

    # endregion

    ExStegoApp().run()

    MessageHelper.save_logs()

