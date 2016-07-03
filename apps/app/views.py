from app import app
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
import pandas as pd
import numpy as np
import os
import glob
import nltk.data
#from __future__ import division  # Python 2 users only
import nltk, re, pprint
from nltk import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from sklearn.metrics.pairwise import linear_kernel
from .forms import LoginForm
import sqlite3

def connect_db():
	return sqlite3.connect('/Users/sheldon/podcasts/test.db')

def create_df_object():
	conn = sqlite3.connect('/Users/sheldon/podcasts/test.db')
	df = pd.read_sql("select * from podcast",conn)
	return df

df = create_df_object()
stop = set(stopwords.words('english'))
tf = TfidfVectorizer(stop_words=stop)
tfidf_matrix = tf.fit_transform(df['transcribed'])
copy_matrix = tf.transform(df['transcribed'])
cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

@app.route('/')
@app.route('/index')
def main():
	conn = sqlite3.connect('/Users/sheldon/podcasts/test.db')
	c = conn.cursor()
	cur = c.execute('select "index", episode, series from podcast')
	db_request = [dict(index=row[0], episode=row[1], series=row[2]) for row in cur.fetchall()]
	return render_template('index.html', data=db_request)

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for OpenID="%s", remember_me="%s' % (form.openid.data, str(form.remember_me.data)))
		return redirect('/index')
	return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/related_podcasts/<int:podcast_id>')
def show_related_podcasts(podcast_id):
		conn = sqlite3.connect('/Users/sheldon/podcasts/test.db')
		c = conn.cursor()
		cur = c.execute('select "index", episode, series from podcast where "index" ={}'.format(podcast_id))
		db_request = [dict(index=row[0], episode=row[1], series=row[2]) for row in cur.fetchall()]
		
		related_pod_index = cosine_similarities.argsort()[podcast_id][::-1]
		pod_dict = dict(zip(range(0, len(related_pod_index)),related_pod_index))
		pod_dict = pd.DataFrame({'rank':pod_dict.keys()}, index=pod_dict.values())
		related_podcasts_df = pd.DataFrame.join(pod_dict, df, how='inner')
		final_df = related_podcasts_df.sort_values('rank')[1:11][['rank','episode','series']]
		related_podcasts = final_df['episode']
		return render_template('related_podcasts.html',original_title=db_request[0]['episode'], data=related_podcasts)

@app.route('/search/<string:query>')
def show_related_podcast(query):
		trans_query = query.lower()
		trans_query = query.split()
		tfidf_matrix_test = tf.fit_transform(trans_query)
		tfidf_matrix_train = tf.transform(df['transcribed'])
		tfidf_matrix_train.todense()
		tfidf_matrix_test.todense()
		query_similarities = linear_kernel(tfidf_matrix_test, tfidf_matrix_train)
		query_similarities = query_similarities.argsort()[0][::-1]
		pod_dict = dict(zip(range(0, len(query_similarities)),query_similarities))
		pod_dict = pd.DataFrame({'rank':pod_dict.keys()}, index=pod_dict.values())
		related_podcasts_df = pd.DataFrame.join(pod_dict, df, how='inner')
	  	final_df = related_podcasts_df.sort_values('rank')[1:11][['rank','episode','series']]
		related_podcasts = final_df['episode']
		return render_template('related_podcasts_to_query.html',original_query=query, data=related_podcasts)