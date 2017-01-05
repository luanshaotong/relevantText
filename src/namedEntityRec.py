#coding=utf-8

try:
    from nltk import ne_chunk, pos_tag, word_tokenize
    from nltk.tree import Tree
except Exception,e :
    count = 1
else:
    count = 0

if count ==0:
    def get_NamedEntity(text):
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        prev = None
        continuous_chunk = []
        current_chunk = []
        for i in chunked:
            if type(i) == Tree:
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue
        return continuous_chunk
else :
    def get_NamedEntity(namestr):
        entities_return = [u"Entity1 1123414",u"Entity2'sdgdsa",u'Entity3"asfgds']
        return entities_return

