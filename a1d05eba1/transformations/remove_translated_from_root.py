from .transformer import TransformerFW

class RemoveTranslatedFromRootFW(TransformerFW):
    def fw(self, content):
        if 'translated' in content:
            (content, translated) = content.popout('translated')
        return content
