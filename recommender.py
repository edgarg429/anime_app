import streamlit as st
import pandas as pd
import numpy as np
from surprise import Reader, Dataset
from surprise.prediction_algorithms import SVD


anime_df = pd.read_csv('./App_data/Top_1000_anime.csv', index_col=0)
user_df = pd.read_csv('./App_data/filtered_user_ratings.csv', index_col=0)
genre_list = pd.read_csv('./App_data/genre_list.csv', index_col=0)
syn_df = pd.read_csv('./App_data/anime_syn_1000.csv', index_col=0)
show_type_list = list(anime_df['Type'].unique()) + ['Anything is fine']
anime_list = list(anime_df['Cleaned_Name'].head(50))+[None]


def Anime_Recommender(user_ratings, anime_df, rec_num, genre=None, show_type=None):
            
    #in the block below the rating_list is appended to the user_rating dataframe, and fit to 
    #an SVD model with the best parameters from the gridsearch
            
    new_ratings_df = user_ratings.append(rating_list, ignore_index=True) 
    reader_rec = Reader(rating_scale=(1,10))
    new_data = Dataset.load_from_df(new_ratings_df, reader_rec)
    svd_ = SVD(n_factors=200, reg_all=0.1, n_epochs=100)
    svd_.fit(new_data.build_full_trainset())
    
    #in the block below the model predicts the rating for every unique anime in the user_ratings
    #dataframe. The prediction is appended to an empty list then sorted by predicted rating 

    
    list_of_anime = []
    for a_id in user_ratings['anime_id'].unique():
        list_of_anime.append((a_id, svd_.predict(userID, a_id)[3]))
    ranked_anime = sorted(list_of_anime, key=lambda x:x[1], reverse=True)
    
    #in the block below, a FOR loop removes anime that the user has already rated from the list
    
    new_ranked_anime = []
    for x in ranked_anime:
        if x[0] in list(rating_list['anime_id']):
            continue
        else:
            new_ranked_anime.append(x)
            
    #in the block below, if a genre is entered, a FOR loop removes all anime that is not 
    #part of the input genre
    
    if genre:
        new_list = []
        genre_list = list(anime_df[anime_df['Genres'].str.contains(genre)]['MAL_ID'])
        for x in new_ranked_anime:
            if x[0] in genre_list:
                new_list.append(x)
            else:
                continue
        new_ranked_anime = new_list
    else:
        pass
    
    #in the block below, if show_type is entered, a FOR loop removes all anime that is not 
    #part of the input show_type
    
    if show_type:
        new_list = []
        type_list = list(anime_df[anime_df['Type'].str.contains(show_type)]['MAL_ID'])
        for x in new_ranked_anime:
            if x[0] in type_list:
                new_list.append(x)
            else:
                continue
        new_ranked_anime = new_list
    else:
        pass
    
    #in the block below, new_ranked_anime is counted, if the list is empty, the user is informed,
    #if the list contains less results than asked, then a separate message is printed and all
    #available results are shown, otherwise, the asked for results are printed 
    
    if len(new_ranked_anime) == 0:
        return st.write('Unfortunately, no results fit your criteria')  
    elif len(new_ranked_anime) < rec_num:
        rec_num = len(new_ranked_anime)
        st.write('Sorry, These are all our results')   
    else:
        pass
    for idx, rec in enumerate(new_ranked_anime):
        title = anime_df.loc[anime_df['MAL_ID'] == int(rec[0])]['Cleaned_Name'].values[0]
        synopsis = syn_df.loc[syn_df['MAL_ID'] == int(rec[0])]['synopsis'].values[0]
        show_type = anime_df.loc[anime_df['MAL_ID'] == int(rec[0])]['Type'].values[0]
        if show_type == 'TV':
            show_type = 'This is a Series'
        elif show_type == 'Music':
            show_type = 'This is a Music Video'
        elif show_type == 'ONA':
            show_type = 'This is an ONA (Original Net Animation)'
        elif show_type == 'OVA':
            show_type = 'This is an OVA (Original Video Animation)'
        st.write(f'Recommendation # {idx+1}: {title}\n                {show_type}\n')
        with st.beta_expander("Expand for Anime synopsis"):
            st.write(synopsis)
        rec_num -= 1
        if rec_num <= 0:
            break



st.title('Anime Otaku Recommendations')

st.header('Please fill out a few detail below')


new_user = st.selectbox('Are you a new User?', ('Yes', 'No', None), index=2, key='a')
if new_user == 'Yes':
    st.write('Welcome!!')
    new_user = True
    userID = user_df['user_id'].max() + 1
    st.write(f'Your userID is: {userID}')
    num_input_key = 1
elif new_user =='No':
    st.write('Welcome Back!!')
    new_user = False
    user_entry = 1
    num_input_key = 1
    if user_entry > 0:
        userID = st.number_input('Please enter User ID', key=str(num_input_key), step=1)
        if userID not in list(user_df['user_id']) or userID == '':
            st.write('User ID not in system')
            st.stop()
        else:
            st.write('Thank You')
            user_entry -= 1

genre = st.selectbox('Did you have a specific genre in mind?', (genre_list.append({'genre':None}, ignore_index=True)), index=42)
    
    
show_type = st.selectbox('What kind of title are you looking for?', (show_type_list), index=6)
if show_type == 'Anything is fine':
    show_type = None
    
    
rating_list = pd.DataFrame()
if new_user == False:
    more_ratings = st.selectbox('Would you like to rate more titles?', ('Yes', 'No', None), key = 'b', index=2)
    if more_ratings == 'No':
        rating_list = rating_list.append(user_df[user_df['user_id']==userID], ignore_index=True)
    elif more_ratings == 'Yes':
        rating_num = st.number_input('How many titles would you like to rate?', key=str(num_input_key+1), min_value=1, max_value=50, step=1)
        num_input_key += 1
        while rating_num > 0:
            num_input_key += 1
            rating_num -= 1
            anime = st.selectbox('Select the title you want to rate', (list(anime_df['Cleaned_Name'].head(50).sort_values())+[None]), key='anime'+str(num_input_key+1), index=50)
            if anime:
                rating = st.selectbox('Rate this anime on a scale of 1-10', (list(range(1,11))+[None]), key ='rate'+str(num_input_key+1), index=10)
                if rating:              
                    rating = int(rating)
                    rating_one_anime = {'user_id':userID,'anime_id':int(anime_df[anime_df['Cleaned_Name']==anime]['MAL_ID']),'rating':rating}
                    rating_list = rating_list.append(rating_one_anime, ignore_index=True)
                    rating_list = rating_list[['user_id','anime_id','rating']]    
    rec_num = st.number_input('How many recommendations would you like?', key='rec'+str(num_input_key+1), step=1, min_value=1, max_value=50)
    if st.button('Get my Recommendations'):
        Anime_Recommender(user_df, anime_df, rec_num, genre=genre, show_type=show_type)
        
        
elif new_user == True:
    st.write('To provide you with recommendations, rate at least one Anime')
    rating_num = st.number_input('How many titles would you like to rate?', key=str(num_input_key+1), min_value=1, max_value=50, step=1)
    num_input_key += 1
    while rating_num > 0:
        num_input_key += 1
        rating_num -= 1
        anime = st.selectbox('Select the title you want to rate', (list(anime_df['Cleaned_Name'].head(50).sort_values())+[None]), key='anime'+str(num_input_key+1), index=50)
        if anime:
            rating = st.selectbox('Rate this anime on a scale of 1-10', (list(range(1,11))+[None]), key ='rate'+str(num_input_key+1), index=10)
            if rating:              
                rating = int(rating)
                rating_one_anime ={'user_id':userID,'anime_id':int(anime_df[anime_df['Cleaned_Name']==anime]['MAL_ID']),'rating':rating}
                rating_list = rating_list.append(rating_one_anime, ignore_index=True)
                rating_list = rating_list[['user_id','anime_id','rating']]    
    rec_num = st.number_input('How many recommendations would you like?', key='rec'+str(num_input_key+1), step=1, min_value=1, max_value=50)
    if st.button('Get my Recommendations'):
        with st.spinner('Calculating Recommendations...'):
            Anime_Recommender(user_df, anime_df, rec_num, genre=genre, show_type=show_type)
        st.balloons()
    
    
    
    