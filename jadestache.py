import pyjade, pyjade.exceptions, pystache


class _JadeLoader(pystache.loader.Loader):
    """
    expands jade of incoming files. Also includes a cache so it doesn't
    read the same file twice
    """
    def __init__(self, *args, **kw):
        pystache.renderer.Loader.__init__(self, *args, **kw)
        self.seen = {} # path : expanded jade
        
    def read(self, path, encoding=None):
        if path in self.seen:
            return self.seen[path]
            
        b = pystache.common.read(path)

        if encoding is None:
            encoding = self.file_encoding

        src = self.unicode(b, encoding)

        expanded = pyjade.utils.process(src)
        self.seen[path] = expanded
        return expanded

class Renderer(pystache.renderer.Renderer):
    """
    pystache renderer that expands base jade syntax on its input
    files. No jade data interpolation happens, so you could use these
    same templates in the browser with js mustache.

    Files need to end with .mustache since it's the mustache loader
    that's going to look for them.
    """
    def __init__(self, *args, **kw):
        debug = False
        if 'debug' in kw:
            debug = kw['debug']
            del kw['debug']
        pystache.renderer.Renderer.__init__(self, *args, **kw)
        self._loader = None if debug else self._new_loader()
            
    def _new_loader(self):
        return _JadeLoader(
                file_encoding=self.file_encoding, extension=self.file_extension,
                to_unicode=self.unicode, search_dirs=self.search_dirs)
        
    def _make_loader(self):
        if self._loader is not None:
            return self._loader
        else:
            # this is for debug mode, to make the templates get reread
            return self._new_loader()
