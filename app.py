import os
import matplotlib.pyplot as plt
from os import path
from wordcloud import WordCloud
import json
import re
from collections import Counter
import random
import math
import copy
from flask import Flask, render_template,url_for,request, Response


app = Flask(__name__)

@app.route('/')
def home():

    return render_template('home.html')

@app.route('/search')
def search():

    if request.method == 'POST':
        user = request.form['comment']
    else:
        user = request.args.get('comment')

    return user

@app.route('/getList')
def getList():

    k=2.0
    b=0.75
    D = 0  # length of document len(text)
    user = search()
    word = user
    searchList = []
    searchList.append(word)

    with open('aalto_avle_dump.txt') as json_file:
        data = json.load(json_file)
        N = len(data)
        listed_title = []
        listed_text = []

        name = "courseName"
        info = "courseInfo"
        score = "courseScore"
        learn = "learningObjectives"
        text_list = []
        for i in range(0,N):
            course_dict = {}
            TF=0
            s=0
            score_sum= 0
            course_list = []

            course = data[i]["courseUnitTexts"]
            course_name = data[i]["nameEn"]
            course_code = data[i]["code"]
            level = course[0]["opasKurssinTaso"]
            text = course[0]["overviewContentDescription"]
            learning = course[0]["overviewLearningOutcomes"]
            D+= len(text)
            code = course_code[0:course_code.find('-')]
            text_lower = learning.lower()
            title_lower = course_name.lower()
            phrase = text_lower.split()
            phrase_set = set(text_lower.split())
            title_set = set(title_lower.split())

            DF=0 #number of courses containing the word
            while s < len(phrase):

                if word == phrase[s]:
                    TF=TF+1
                    s=s+1
                else:
                    s=s+1

            if TF==0:
                BM25_perWord = 0
                score_sum = 0
            else:
                course_list.append(TF)
                course_list.append(text)
                course_dict[name] = course_name
                course_dict[info] = course_list
                course_dict[learn] = learning
                if course_dict not in listed_text:
                    listed_text.append(course_dict)

            L = (D/N)
            DF = len(listed_text)
            IDF_log = (N-DF + 0.5)/(DF+5)
            IDF = math.log10(IDF_log) #inverse document frequency of word q given
            BM25_perWord = (IDF*TF*(k+1))/(TF+k*(1-b+b*(D/L)))
            BMM25_value = copy.copy(BM25_perWord)
            score_sum = BMM25_value
            course_dict[score] = score_sum

    newlist = sorted(listed_text, key=lambda k: k['courseScore'], reverse=True)

    new_list = newlist.copy()

    return new_list


@app.route('/listWords')

def listWords():


    newlist = getList()
    sanakirja = {}

    text_code = ""
    for item in newlist:
        text_code += " " + item['courseName']

    word_counter = {}
    split_it = text_code.lower().split()

    for word in split_it:
        top = re.sub('[?.,!/)(;:-]', '', word)
        if top in word_counter:
            word_counter[top] += 1
        else:
            word_counter[top] = 1

    popular_words = sorted(word_counter, key=word_counter.get, reverse=True)

    top_50 = popular_words[:50]

    topped = []
    not_these = ["in", "assignment", "studies","content","aided", "varying", "iii", "from", "part", "and", "of", "for", "into", "-", "a",
                 "ja", "with", "to", "the", "och", "de", "en", "an", "will", "able", "on"]

    def wrong_words(sana):
        if sana not in not_these:
            return sana
        else:
            return "-"

    for top in top_50:
        if len(top) > 2:
            sanatulos = wrong_words(top)
            if sanatulos not in topped:
                topped.append(sanatulos)

    final = []
    for i in topped:
        if i != "-":
            final.append(i)


    return newlist, final
# return render_template('home.html',positio = positio, start_list = newlist, words = final, prediction = result_list)

@app.route('/printWords', methods = ['GET', 'POST'])
# @app.route('/predict', methods = ['GET', 'POST'])
def printWords():
    newlist, final = listWords()

    user = search()
    finaali = mummo()
    for i in final:
        pos = i
    newlist2 = newlist[0:5]
    return render_template('home.html',user= user, positio = pos, start_list = newlist2, words = final)

@app.route('/mummo')
def mummo():
    #
    # if pos == None:
    #     pos = "and"
    # else:
    #     pos = selection()
    newlist, final = listWords()

    for j in final:
        pos = j

    selection = pos
    word = []
    word.append(selection)

    listed_title2 = []
    listed_text2 = []

    name = "courseName"
    info = "courseInfo"
    score = "courseScore"
    learn = "learningObjectives"

    text_list2 = []
    priority_list = []
    second_list = []
    third_list = []


    listed_course = newlist

    for x in listed_course:
        course_dict = {}
        text_dict = {}
        text_dict_third = {}

        course_name = x["courseName"]
        course_info = x["courseInfo"]
        course_score = x["courseScore"]
        course_learn = x["learningObjectives"]

        title_lower = course_name.lower()
        learn_lower = course_learn.lower()
        lear = learn_lower.split()
        title_set = set(title_lower.split())
        learning_set = set(learn_lower.split())

        word_set = set(word)

        if word_set.intersection(title_set):
            course_dict[name] = course_name
            course_dict[info] = course_info
            course_dict[score] = course_score
            if course_dict not in priority_list:
                priority_list.append(course_dict)

        if word_set.intersection(learning_set):
            text_dict[name] = course_name
            text_dict[info] = course_info
            text_dict[score] = course_score
            if text_dict not in second_list:
                second_list.append(text_dict)

    final_courses = sorted(priority_list, key=lambda k: k['courseScore'], reverse=True)
    courses_second = sorted(second_list, key=lambda k: k['courseScore'], reverse=True)

    result_list = []

    for f in final_courses[0:3]:
        if f not in result_list:
            result_list.append(f)

    for g in courses_second[0:6]:
        if g not in result_list:
            result_list.append(g)

    finaali = result_list[:]

    return finaali

@app.route('/newPage', methods = ['GET', 'POST'])
def newPage():

    pos, finaali = mummo()
    return render_template('home.html', response=selection(), pred = finaali)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, threaded=True)
