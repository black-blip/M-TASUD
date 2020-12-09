class Summarizer():
    
    def __init__(self, document, summarization_tool="sumy", summarization_method="lsa", num_sentences=20, reduction_perc=80, language="english"):
        self.document = document
        self.summarization_tool = summarization_tool
        self.summarization_method = summarization_method
        self.num_sentences = num_sentences
        self.summary_perc = 100 - reduction_perc
        self.language = language
        self.summary = ""
    
    def preprocess(self):
        if(self.summarization_tool=="sumy"):
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.nlp.tokenizers import Tokenizer
            parser = PlaintextParser.from_string(self.document, Tokenizer(self.language))
            return parser

    def summarize(self):
        if(self.summarization_tool=="sumy"):
            from sumy.nlp.stemmers import Stemmer
            from sumy.utils import get_stop_words
            parser = self.preprocess()
            stemmer = Stemmer(self.language)
            if(self.summarization_method=="lsa"):
                from sumy.summarizers.lsa import LsaSummarizer
                summarizer = LsaSummarizer(stemmer)
            elif(self.summarization_method=="lexrank"):
                from sumy.summarizers.lex_rank import LexRankSummarizer
                summarizer = LexRankSummarizer(stemmer)
            elif(self.summarization_method=="textrank"):
                from sumy.summarizers.text_rank import TextRankSummarizer
                summarizer = TextRankSummarizer(stemmer)
            summarizer.stop_words = get_stop_words(self.language)
            for sentence in summarizer(parser.document, self.num_sentences):
                self.summary += str(sentence)
            return self.summary
        else:
            return ""  
