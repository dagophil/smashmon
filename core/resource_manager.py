import pygame
import logging


class SingletonExistsException(Exception):
    """
    This exception is thrown when a singleton is to be created but it already existed.
    """

    def __init__(self, *args, **kwargs):
        super(SingletonExistsException, self).__init__(*args, **kwargs)


class ResourceManager(object):
    """
    Manages all loadable files (such as images, sounds, ...).
    This is a singleton class, meaning that you must not create more than one instance of this class.
    """

    __instance = None

    def __init__(self):
        if ResourceManager.__instance is not None:
            raise SingletonExistsException("Tried to create a ResourceManager, but there already is one.")
        ResourceManager.__instance = self
        self._images = {}

    @staticmethod
    def instance():
        if ResourceManager.__instance is None:
            ResourceManager.__instance = ResourceManager()
        return ResourceManager.__instance

    def get_image(self, filename, size=None):
        if size is None:
            size = (0, 0)
        if (filename, size) not in self._images:
            try:
                logging.debug("Loading image from file: %s" % filename)
                im = pygame.image.load(filename).convert()
            except pygame.error:
                raise IOError("File %s not found." % filename)
            if size != (0, 0):
                logging.debug("Resizing image %s to (%d, %d)" % (filename, size[0], size[1]))
                im = pygame.transform.scale(im, size)
            self._images[(filename, size)] = im
            return im
        else:
            return self._images[(filename, size)]
