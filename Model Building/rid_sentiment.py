import re
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud, STOPWORDS 
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
from nltk.corpus import sentiwordnet as swn
from nltk.tokenize import word_tokenize



def clean_tweet(tweet):
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r'[^a-zA-Z\s]', '', tweet)
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(tweet)
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words and len(word) > 1]
    
    return ' '.join(filtered_words)


def wrangle_adidas_data(data):
    data = data.copy()
    data.ReviewInfo.fillna("No Info", inplace=True)
   
    users = []
    dates = []
    verifys = []
    reviews= []

    for dat in data["ReviewInfo"]:
        if dat is not "No Info":
            #iterate through on several conditions
            if dat is not None:
                dat_split = dat.split("|")
                if len(dat_split) >= 4:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    verifys.append(True)
                    reviews.append(True)
                elif len(dat_split) == 3:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    if dat_split[2] == ' Verified Purchaser ':
                        verifys.append(True)
                        reviews.append(False)
                    else:
                        verifys.append(False)
                        reviews.append(True)
                else:
                    users.append(dat_split[0])
                    dates.append(dat_split[1])
                    verifys.append(False)
                    reviews.append(False)

            else:
                users.append(None)
                dates.append(None)
                verifys.append(False)
                reviews.append(False)
        else:
            users.append(None)
            dates.append(None)
            verifys.append(False)
            reviews.append(False)
    data["UserID"] = users 
    data["Date"] = dates
    data["VerifiedPurchaser"] = verifys
    data["IncentivizedReview"] = reviews

    data.drop(columns="ReviewInfo", inplace=True)
    data["Price"].astype(int)
    data["ColoursAvailable"].astype(int)
    data.UserID.fillna("Unknown", inplace=True)
    data.Reviews.fillna("No Topic", inplace=True)
    
    return data


def show_wordcloud(data, stylish=False, logo=None):
    if stylish:
        allWords = ' '.join([tweets for tweets in data])

        wordCloud = WordCloud(background_color='white',
                              max_words=10000,
                              mask=logo,
                              contour_width=1,
                              contour_color='black')
        wordCloud.generate(allWords)
        fig = plt.figure(figsize=(10,10))

        plt.imshow(wordCloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
        
    else:
        allWords = ' '.join([str(tweets) for tweets in data])
        wordCloud = WordCloud(background_color='white',
                              max_words=10000,
                              contour_width=1,
                              contour_color='black')

        # generate the word cloud
        wordCloud.generate(allWords)

        # display the word cloud
        fig = plt.figure(figsize=(20,20))

        plt.imshow(wordCloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
        

def get_vader_scores(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    
    return sentiment['pos'], sentiment['neg'], sentiment['neu'], sentiment['compound']


def show_compound_view(data, rating_column):
    #plot visualisation
    ax = sns.barplot(data=data, x='Rating', y=rating_column)
    ax.set_title(f'Varying  Average Rating By {rating_column}')
    plt.show()
    
    
def show_all_scores(data, pos, neu, neg):
    fig, axs = plt.subplots(1, 3, figsize=(12, 3))
    sns.barplot(data=data, x='Rating', y=pos, ax=axs[0])
    sns.barplot(data=data, x='Rating', y=neu, ax=axs[1])
    sns.barplot(data=data, x='Rating', y=neg, ax=axs[2])
    axs[0].set_title('Positive')
    axs[1].set_title('Neutral')
    axs[2].set_title('Negative')
    plt.tight_layout()
    plt.show()
    
       
def get_textblob_scores(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0:
        return polarity, 0, 0, 'positive', polarity
    elif polarity < 0:
        return 0, abs(polarity), 0, 'negative', polarity
    else:
        return 0, 0, 0, 'neutral', polarity

    
    
# Define a mapping from NLTK POS tags to SentiWordNet POS tags
def get_sentiment(word, pos):
    if pos.startswith('J'):
        pos = 'a'
    elif pos.startswith('V'):
        pos = 'v'
    elif pos.startswith('N'):
        pos = 'n'
    elif pos.startswith('R'):
        pos = 'r'
    else:
        pos = None

    if pos:
        return list(swn.senti_synsets(word, pos))
    else:
        return []

def get_sentiwordnet_scores(text):
    pos_score = 0.0
    neg_score = 0.0
    neu_score = 0.0
    tokens_count = 0
    
    # Tokenize and tag parts of speech
    for word, pos in nltk.pos_tag(word_tokenize(text)):
        synsets = get_sentiment(word, pos)
        if synsets:
            synset = synsets[0]
            pos_score += synset.pos_score()
            neg_score += synset.neg_score()
            neu_score += synset.obj_score()
            tokens_count += 1
    
    if tokens_count == 0:
        return 0.0, 0.0, 0.0
    
    pos_score /= tokens_count
    neg_score /= tokens_count
    neu_score /= tokens_count
    
    return pos_score, neg_score, neu_score

def show_pairplot(df):
    df_cleaned = df.drop_duplicates()
    df_cleaned.reset_index(drop=True, inplace=True)
    sns.pairplot(data=df_cleaned,
                 vars=['Vader_Neg', 'Vader_Neu', 'Vader_Pos',
                       'TextBlob_Neg', 'TextBlob_Neu', 'TextBlob_Pos',
                       'SentiWordNet_Neg', 'SentiWordNet_Neu', 'SentiWordNet_Pos'],
                hue='Rating', 
                palette='tab10')
    plt.show()



def show_sentiment_score_comparison(data):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data[['Vader_Neg', 'Vader_Neu', 'Vader_Pos',
                       'TextBlob_Neg', 'TextBlob_Neu', 'TextBlob_Pos',
                       'SentiWordNet_Neg', 'SentiWordNet_Neu', 'SentiWordNet_Pos']])
    plt.title('Sentiment Scores Comparison')
    plt.xticks(rotation=45)
    plt.show()
    
def show_polarity_heatmap(data):
    correlation = data[['Vader_Polarity', 'TextBlob_Polarity', 'SentiWordNet_Polarity']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation, annot=True, cmap='coolwarm')
    plt.title('Sentiment Scores Correlation')
    plt.show()
    
def show_polarity_scores(data, sent1, sent2, size=12):
    plt.figure(figsize=(12, 6))
    plt.subplot(131)
    sns.scatterplot(x=f'{sent1}_Neg', y=f'{sent2}_Neg', data=data)
    plt.title(f'Negative Polarity Comparison ({sent1} vs {sent2})', fontsize=size)
    plt.subplot(132)
    sns.scatterplot(x=f'{sent1}_Neu', y=f'{sent2}_Neu', data=data)
    plt.title(f'Neutral Polarity Comparison ({sent1} vs {sent2})', fontsize=size)
    plt.subplot(133)
    sns.scatterplot(x=f'{sent1}_Pos', y=f'{sent2}_Pos', data=data)
    plt.title(f'Positive Polarity Comparison ({sent1} vs {sent2})', fontsize=size)
    plt.tight_layout(pad=0)
    plt.show()
    
    
def show_violinplot(df):
    plt.figure(figsize=(14, 6))
    plt.subplot(131)
    sns.violinplot(data=df[['Vader_Neg', 'Vader_Neu', 'Vader_Pos']])
    plt.title('VADER Sentiment Distribution')
    plt.subplot(132)
    sns.violinplot(data=df[['TextBlob_Neg', 'TextBlob_Neu', 'TextBlob_Pos']])
    plt.title('TextBlob Sentiment Distribution')
    plt.subplot(133)
    sns.violinplot(data=df[['SentiWordNet_Neg', 'SentiWordNet_Neu', 'SentiWordNet_Pos']])
    plt.title('SentiWordNet Sentiment Distribution')
    plt.tight_layout()
    plt.show()

    
def show_barplot(df):
    average_scores = df[['Vader_Polarity', 'TextBlob_Polarity', 'SentiWordNet_Polarity']].mean()
    plt.figure(figsize=(8, 5))
    sns.barplot(x=average_scores.index, y=average_scores.values, palette='viridis')
    plt.title('Average Sentiment Scores Comparison')
    plt.xlabel('Sentiment Analysis Tool')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)
    plt.show()
    

def show_distribution_column(df):
    sentiment_columns = ['Vader_Pos', 'Vader_Neg', 'Vader_Neu',
                         'TextBlob_Pos', 'TextBlob_Neg', 'TextBlob_Neu',
                         'SentiWordNet_Pos', 'SentiWordNet_Neg', 'SentiWordNet_Neu']

    plt.figure(figsize=(12, 8))
    for i, col in enumerate(sentiment_columns):
        plt.subplot(3, 3, i+1)
        sns.histplot(df[col], kde=True, color='blue')
        plt.title(col)
        plt.tight_layout()

    plt.show()

    
def show_kdeplot(df): 
    plt.figure(figsize=(8, 5))
    sns.histplot(df[['Vader_Polarity', 'TextBlob_Polarity', 'SentiWordNet_Polarity']].mean(axis=1), kde=True, color='green')
    plt.title('Overall Sentiment Polarity Distribution')
    plt.xlabel('Overall Polarity Score')
    plt.ylabel('Frequency')
    plt.show()