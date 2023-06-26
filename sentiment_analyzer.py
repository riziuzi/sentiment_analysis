import os
import re
import pandas as pd
from nltk import word_tokenize
import syllables
import requests
from bs4 import BeautifulSoup
from progress_bar import Progress


class Scraper:
    def __init__(self, input_data_path='Input.xlsx'):
        self.scrapped_data_path = "./Scrapped_Data"
        self.separator = "###SEPARATOR###"
        self.input_data_path = input_data_path
        try:
            self.input_data = pd.read_excel(self.input_data_path)
        except:
            print("Please keep the Input.xlsx file and mention the path (Recommended: Put your Input.xlsx file in root directory)")
            return
        self.make_directory(self.scrapped_data_path)

    def run_scraper(self):
        """
        Runs the web scraper for each URL in the input data and displays a progress bar.
        """
        total_urls = len(self.input_data)
        pbar = Progress(total_iterations=total_urls)
        print("\nData scrapping started!")
        pbar.start()
        for i in range(total_urls):
            url_id, url = self.input_data.iloc[i, 0], self.input_data.iloc[i, 1]
            heading, text = self.scrape_article(url=url)
            self.absentee_check(url_id, url, heading, text)
            self.save_txt(name=url_id, content=f"heading:{heading}\n{self.separator}\ntext:{text}",
                            path=self.scrapped_data_path)
            pbar.update(1)
        print(f"Scrapped article's text and heading in .txt file in {self.scrapped_data_path}")

    def scrape_article(self, url):
        """
        Scrapes the web page at the given URL to extract the heading and text.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        unwanted_tags = soup.select("script, style")
        for tag in unwanted_tags:
            tag.extract()

        heading = ""
        try:
            heading = soup.select_one("[class*='td-parallax-header'] h1").get_text()
        except AttributeError:
            pass

        try:
            heading = soup.select_one("[class*='tdb_title'] h1").get_text()
        except AttributeError:
            pass

        article = ""
        try:
            articles = soup.select("[class*='td-post-content'] p")
            article = '\n\n'.join([p.get_text() for p in articles])
        except AttributeError:
            pass

        return heading, article

    def save_txt(self, name, content, path):
        """
        Saves the scraped content to a text file.
        """
        with open(os.path.join(path, f"{name}.txt"), 'w', encoding='utf-8') as file:
            file.write(content)

    def absentee_check(self, url_id, url, heading, text):
        """
        Checks if the heading and/or text are missing and updates the "absentee" Excel file accordingly.
        """
        if not heading and not text:
            if not os.path.exists("absentee.xlsx"):
                data = pd.DataFrame(columns=["url_id", "url", "heading", "text"])
                data.to_excel("absentee.xlsx")
            data = pd.read_excel("absentee.xlsx").drop('Unnamed: 0', axis=1)
            new_row = pd.Series([url_id, url, 0, 0], index=data.columns)
            data = pd.concat([data, new_row.to_frame().transpose()], ignore_index=True)
            data.to_excel("absentee.xlsx")

        elif not text:
            if not os.path.exists("absentee.xlsx"):
                data = pd.DataFrame(columns=["url_id", "url", "heading", "text"])
                data.to_excel("absentee.xlsx")
            data = pd.read_excel("absentee.xlsx").drop('Unnamed: 0', axis=1)
            new_row = pd.Series([url_id, url, 1, 0], index=data.columns)
            data = pd.concat([data, new_row.to_frame().transpose()], ignore_index=True)
            data.to_excel("absentee.xlsx")

    def make_directory(self, directory):
        """
        Creates the directory if it doesn't exist.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
class SentimentAnalysis:
    def __init__(self, stop_path = "./StopWords/", separator="###SEPARATOR###",master_path = "./MasterDictionary/"):
        self.stop_words = ["heading", "text", "", " "]
        self.stop_path = stop_path
        self.master_path = master_path
        if(os.path.isdir(self.master_path)):
            pass
        else:
            print("master dictionary directory not found. Must: put dictionaries.txt files in a folder. Recommended: in ./MasterDictionary/")
            return
        if(os.path.isdir(self.stop_path)):
            pass
        else:
            print("stop words directory not found. Must: put stopword.txt files in a folder. Recommended: in ./StopWords/")
            return

        self.master_words = []
        self.np_words = {}
        self.negative_words = []
        self.positive_words = []
        self.syllables_library = True
        self.separator = separator
        self.separators = [self.separator, "\n", " ", ":", '“', ".", "”"]
        
        
        # Storing repeated usable data (Once computed, no need to compute each time, for each file)
        self.positive_score = None
        self.negative_score = None
        self.word_count = None
        self.tokens = None
        self.text = None
        self.unfiltered_text = None
        self.complex_count = None
        self.percentage_of_complex_words = None
        self.average_sentence_length = None
        self.text_path = None
        
    def calculate_polarity_score(self, text_path):
        self.text_path
        text = None
        words = None
        self.separators = [self.separator, "\n", " ", ":", '“', ".", "”"]
        with open(text_path, 'r', encoding="utf-8") as file:
            full_file = file.read()
            text = full_file.split(self.separator)[1]
            words = re.split("|".join(map(re.escape, self.separators)), text)
            filtered_text = [w for w in words if (w.isalpha() and not w.lower() in set(self.stop_words)) or w in set(self.master_words)]

        tokens = word_tokenize(" ".join(filtered_text))

        positive_score = 0
        negative_score = 0
        word_count = 0

        for token in tokens:
            if token.lower() in self.positive_words:
                positive_score += 1
            elif token.lower() in self.negative_words:
                negative_score += 1
            word_count += 1

        polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
        self.positive_score = positive_score
        self.negative_score = negative_score
        self.word_count = word_count
        self.text = text
        self.unfiltered_text = words
        self.tokens = tokens
        return positive_score, negative_score, polarity_score

    def load_stop_words(self):
        for filename in os.listdir(self.stop_path):
            file_path = os.path.join(self.stop_path, filename)
            if os.path.isfile(file_path): 
                with open(file_path, 'r') as file:
                    stop = list(set(file.read().split()))
                    self.stop_words.extend(stop)

    def load_master_dictionary(self):
        for filename in os.listdir(self.master_path):
            file_path = os.path.join(self.master_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    words = file.read().split()
                    self.master_words.extend(words)
                    self.np_words[filename] = words
        self.negative_words = self.np_words.get(list(self.np_words.keys())[0], [])
        self.positive_words = self.np_words.get(list(self.np_words.keys())[1], [])

    def subjectivity(self):
        if(self.word_count == None):
            print("first run instance.calculate_polarity_score if you have not run this earlier")
        else:
            return (self.positive_score + self.negative_score) / (self.word_count + 0.000001)

    def average_sentence_length_fun(self):              # same as average number of words per sentence
        if(self.text == None):
            print("first run instance.calculate_polarity_score() if you have not run this earlier")
        else:
            sentences = re.split(r'[.!?]+', self.text)
            self.average_sentence_length = sum(len(word_tokenize(sentence)) for sentence in sentences) / len(sentences)
            return self.average_sentence_length
    
    def complex_count_fun(self):
        if(self.tokens == None):
            print("first run instance.calculate_polarity_score() if you have not run this earlier")
        else:
            self.complex_count =  sum(1 for token in self.tokens if len(token) > 2 and token.isalpha() and token.lower() not in set(self.stop_words) and self.count_syllables(token) > 2)
            return self.complex_count

    def percentage_of_complex_words_fun(self):
        if(self.complex_count == None):
            self.complex_count_fun()
            return self.percentage_of_complex_words_fun()
        elif(self.tokens == None):
            self.calculate_polarity_score(self.text_path)
            return self.percentage_of_complex_words_fun()
        else:
            self.percentage_of_complex_words = self.complex_count/len(self.tokens) if len(self.tokens) else 0
            return self.percentage_of_complex_words
    
    def fog_index(self):
        if (self.percentage_of_complex_words == None):
            self.percentage_of_complex_words_fun() 
            return self.fog_index()
        elif(self.average_sentence_length==None):
            self.average_sentence_length_fun()
            return self.fog_index()
        else:
            return 0.4*(
                self.percentage_of_complex_words +
                self.average_sentence_length)
        
    def count_syllables(self, word):
        if (self.syllables_library):            
            return syllables.estimate(word)
        vowels = "aeiouAEIOU"                   
        count = 0
        prev_char = None

        for char in word:
            if char in vowels:
                if prev_char and prev_char not in vowels:
                    count += 1
            prev_char = char

        if word.endswith("e"):
            count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            count += 1

        return max(1, count)
    
    def average_syllable_per_word_fun(self):
        if(self.tokens==None):
            self.calculate_polarity_score(self.text)
        count_syllable = 0
        number_of_word = 0
        for token in self.tokens:
            count_syllable+= self.count_syllables(token)
            number_of_word+=1
        return int(count_syllable/number_of_word) if(number_of_word) else 0
    
    def word_count_fun(self):
        if(self.word_count == None):
            self.calculate_polarity_score(self.text_path)
        else:
            return self.word_count
        
    def personal_pronoun_count(self):
        pronouns_pattern = r"\b(I|me|my|mine|myself|you|your|yours|yourself|yourselves|he|him|his|himself|she|her|hers|herself|it|its|itself|we|us|our|ours|ourselves|they|them|their|theirs|themselves)\b"
        matches = re.findall(pronouns_pattern, " ".join(self.unfiltered_text), flags=re.IGNORECASE)
        stop_match = ["US", "IT"]
        filtered_matches = [match for match in matches if match not in stop_match]
        pronoun_count = len(filtered_matches)                  
        return pronoun_count
    
    def average_word_length(self):
        count_word = 0
        word_length_sum = 0

        for word in sa.unfiltered_text:
            if word.isalpha():
                count_word+=1
                word_length_sum+=len(word)
        return int(word_length_sum/count_word) if count_word !=0 else 0
    
    def reset(self):
        self.positive_score = None
        self.negative_score = None
        self.word_count = None
        self.tokens = None
        self.text = None
        self.unfiltered_text = None
        self.complex_count = None
        self.percentage_of_complex_words = None
        self.average_sentence_length = None
        self.text_path = None
    







if __name__ == "__main__":
    
    scraper = Scraper()             # Scrapping in a nutshell
    scraper.run_scraper()
    
    # Create an instance of SentimentAnalysis
    sa = SentimentAnalysis()

    # Load stop words and master dictionary
    sa.load_stop_words()
    sa.load_master_dictionary()

    # Define the Scrapped_Data folder path
    folder_path = "./Scrapped_Data/"

    # Read the input file
    input_file = 'Input.xlsx'
    absentee_file = 'absentee.xlsx'
    df_input = pd.read_excel(input_file)
    df_absentee = pd.read_excel(absentee_file)

    # Initialize lists to store the results
    urls = []
    url_ids = []
    positive_scores = []
    negative_scores = []
    polarity_scores = []
    data = {}

    columns = ['URL_ID',
    'URL',
    'POSITIVE SCORE',
    'NEGATIVE SCORE',
    'POLARITY SCORE',
    'SUBJECTIVITY SCORE',
    'AVG SENTENCE LENGTH',
    'PERCENTAGE OF COMPLEX WORDS',
    'FOG INDEX',
    'AVG NUMBER OF WORDS PER SENTENCE',
    'COMPLEX WORD COUNT',
    'WORD COUNT',
    'SYLLABLE PER WORD',
    'PERSONAL PRONOUNS',
    'AVG WORD LENGTH']

    df = pd.DataFrame(columns=columns)

    pbar = Progress(total_iterations=len([file_name for file_name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]))
    print("Data analysis started!\n")
    pbar.start()
    for filename in os.listdir(folder_path):
        text_path = os.path.join(folder_path, filename)
        if os.path.isfile(text_path):
            url_id = os.path.splitext(filename)[0]
            row = df_input[df_input['URL_ID'] == int(url_id)]
            url = row.iloc[0]['URL']
            if not (url_id in df_absentee['url_id'].values):
                sa.reset()
                sa.separator = "###SEPARATOR###"
                positive_scores, negative_scores, polarity_scores = sa.calculate_polarity_score(text_path=text_path)
                hellll = sa.percentage_of_complex_words_fun()
                data = {
                    'URL_ID': url_id,
                    'URL': url,
                    'POSITIVE SCORE': positive_scores,
                    'NEGATIVE SCORE': negative_scores,
                    'POLARITY SCORE': polarity_scores,
                    'SUBJECTIVITY SCORE': sa.subjectivity(),
                    'AVG SENTENCE LENGTH': sa.average_sentence_length_fun(),
                    'PERCENTAGE OF COMPLEX WORDS': hellll,
                    'FOG INDEX': sa.fog_index(),
                    'AVG NUMBER OF WORDS PER SENTENCE':sa.average_sentence_length_fun(), 
                    'COMPLEX WORD COUNT': sa.complex_count_fun(),
                    'WORD COUNT': sa.word_count_fun(),
                    'SYLLABLE PER WORD': sa.average_syllable_per_word_fun(),
                    'PERSONAL PRONOUNS': sa.personal_pronoun_count(),
                    'AVG WORD LENGTH': sa.average_word_length()
                }
            else:
                data = {
                        'URL_ID': url_id,
                        'URL': url,
                        'POSITIVE SCORE': None,
                        'NEGATIVE SCORE': None,
                        'POLARITY SCORE': None,
                        'SUBJECTIVITY SCORE': None,
                        'AVG SENTENCE LENGTH': None,
                        'PERCENTAGE OF COMPLEX WORDS': None,
                        'FOG INDEX': None,
                        'AVG NUMBER OF WORDS PER SENTENCE':None, 
                        'COMPLEX WORD COUNT': None,
                        'WORD COUNT': None,
                        'SYLLABLE PER WORD': None,
                        'PERSONAL PRONOUNS': None,
                        'AVG WORD LENGTH': None
                    }
        pbar.update(1)
        data = {key: pd.to_numeric(value, errors='coerce') if key != 'URL' else value for key, value in data.items()}
        df.loc[len(df)] = data

    
    output_file = 'Output.xlsx'
    df_sorted = df.sort_values("URL_ID")
    df_sorted.to_excel(output_file, index=False)
    print("Data analysis ended\n")
    print("Output file '{}' created successfully.".format(output_file))
