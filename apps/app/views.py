from app import app
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from .forms import LoginForm
import pandas as pd
import numpy as np
import os
import glob
from nltk.corpus import stopwords
from gensim import corpora, models, similarities
import gensim
import sqlite3

dictionary = corpora.Dictionary.load('models/words.dict')
corpus = corpora.MmCorpus('models/corpus.mm')
tfidf = gensim.models.tfidfmodel.TfidfModel.load('models/tfidf_model')
lsi = gensim.models.lsimodel.LsiModel.load('models/model.lsi')
index = similarities.MatrixSimilarity.load('models/corpus.index')
corpus_tfidf = tfidf[corpus]
corpus_lsi = lsi[corpus_tfidf]

def connect_db():
	return sqlite3.connect('/Users/sheldon/podcasts/test.db')

def create_df_object():
	conn = sqlite3.connect('/Users/sheldon/podcasts/test.db')
	df = pd.read_sql("select * from podcast",conn)
	return df

df = create_df_object()
stop = set(stopwords.words('english'))

@app.route('/index')
@app.route('/', methods = ['GET','POST'])
def main():
	if request.method == "POST":
		query = request.form.get('search','default value')
		return redirect('/search/{}'.format(query))
	else:
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
	def get_related_podcasts(index):

		def getKey(item):
			return item[1]

		corpus = corpus_lsi[index]
		corpus = sorted(corpus, key=getKey, reverse=True)[0:10]
		related_df = pd.DataFrame(corpus,columns=['index','score'])
		final_df = pd.merge(related_df, df, on='index')[['index','episode','score','series']]
		return final_df
	final_df = get_related_podcasts(podcast_id)
	related_podcasts = final_df['episode']
	return render_template('related_podcasts.html',original_title=db_request[0]['episode'], data=related_podcasts)

@app.route('/search/<string:query>')
def show_related_podcast_query(query):
	trans_query = query.lower()
	trans_query = query.split()
	def get_related_podcasts_query(query):
	    vec_box = dictionary.doc2bow(query.split())
	    vec_lsi = lsi[vec_box]
	    sims = index[vec_lsi]
	    sims = sorted(enumerate(sims), key=lambda item: -item[1])[0:10]
	    related_df = pd.DataFrame(sims,columns=['index','score'])
	    final_df = pd.merge(related_df, df, on='index')[['index','episode','score','series']]
	    return final_df
	related_podcasts = get_related_podcasts_query(query)
	related_podcasts = related_podcasts['episode']
	return render_template('related_podcasts_to_query.html',original_query=query, data=related_podcasts)