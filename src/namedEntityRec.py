#coding=utf-8

try:
    from nltk import ne_chunk, pos_tag, word_tokenize
    from nltk.tree import Tree
    #raise 1
except Exception,e :
    count = 1
else:
    count = 0

if count ==0:
    def get_NamedEntity(text):
        print ("get_NamedEntity count ==0")
        print ("chunked: ")
        print ne_chunk(pos_tag(word_tokenize(text)))
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        # print type(chunked)
        # print "len of chunked: " + str(len(chunked))
        prev = None
        continuous_chunk = []
        current_chunk = []
        # if len(chunked) == 1:
        #     current_chunk.append(" ".join([token for token, pos in chunked.leaves()]))
        #     named_entity = " ".join(current_chunk)
        #     if named_entity not in continuous_chunk:
        #         continuous_chunk.append(named_entity)
        # else:
        for i in chunked:
            print ("i: ")
            print i
            print type(i)
            if type(i) == Tree:
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            #     print ("current_chunk: ")
            #     print current_chunk
            # elif current_chunk:
            #     print ("elif current_chunk: ")
            #     print current_chunk
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                # print ("else: ")
                # print current_chunk
                continue
        return continuous_chunk
else :
    def get_NamedEntity(namestr):
        entities_return = [u"Hong Kong",u"England"]
        return entities_return

