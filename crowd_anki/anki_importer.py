import json
import shutil
from thirdparty.pathlib import Path

import aqt
import aqt.utils

from crowd_anki.utils.constants import DECK_FILE_EXTENSION, MEDIA_SUBDIRECTORY_NAME
from crowd_anki.representation.deck import Deck


class AnkiJsonImporter(object):
    def __init__(self, collection):
        self.collection = collection

    def load_from_file(self, file_path):
        """
        Load deck from json file
        :type file_path: Path
        """
        if not file_path.exists():
            raise ValueError("There is no {} file inside of the selected directory".format(file_path.name))

        with file_path.open() as deck_file:
            deck_json = json.load(deck_file)
            deck = Deck.from_json(deck_json)

            deck.save_to_collection(self.collection)

    def load_from_directory(self, directory_path, import_media=True):
        """
        Load deck serialized to directory
        Assumes that deck json file is located in the directory and named
        same way as a directory but with json file extension.
        :param import_media: Should we copy media?
        :type directory_path: Path
        """
        if aqt.mw:
            aqt.mw.backup()
            aqt.mw.progress.start(immediate=True)

        try:
            self.load_from_file(directory_path.joinpath(directory_path.name).with_suffix(DECK_FILE_EXTENSION))

            if import_media:
                media_directory = directory_path.joinpath(MEDIA_SUBDIRECTORY_NAME)
                if media_directory.exists():
                    for filename in media_directory.iterdir():
                        shutil.copy(str(filename.resolve()), self.collection.media.dir())
                else:
                    print ("Warning: no media directory exists.")
        finally:
            if aqt.mw:
                aqt.mw.progress.finish()
                aqt.mw.deckBrowser.show()

    @staticmethod
    def import_deck(collection, directory_path, import_media=True):
        importer = AnkiJsonImporter(collection)
        try:
            importer.load_from_directory(directory_path, import_media)
            aqt.utils.showInfo("Import of {} deck was successful".format(directory_path.name))
        except ValueError as error:
            aqt.utils.showWarning(error.args[0])