# Importing essential libraries
from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import json

app = Flask(__name__)


import pandas as pd
import numpy as np
import tensorflow as tf

data=pd.read_csv('recipes.csv')

dataset=data.copy()
columns=['RecipeId','Name','CookTime','PrepTime','TotalTime','RecipeIngredientParts','Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent','RecipeInstructions']
dataset=dataset[columns]



max_Calories=2000
max_daily_fat=100
max_daily_Saturatedfat=13
max_daily_Cholesterol=300
max_daily_Sodium=2300
max_daily_Carbohydrate=325
max_daily_Fiber=40
max_daily_Sugar=40
max_daily_Protein=200
max_list=[max_Calories,max_daily_fat,max_daily_Saturatedfat,max_daily_Cholesterol,max_daily_Sodium,max_daily_Carbohydrate,max_daily_Fiber,max_daily_Sugar,max_daily_Protein]




extracted_data=dataset.copy()
for column,maximum in zip(extracted_data.columns[6:15],max_list):
    extracted_data=extracted_data[extracted_data[column]<maximum]



from sklearn.preprocessing import StandardScaler
scaler=StandardScaler()
prep_data=scaler.fit_transform(extracted_data.iloc[:,6:15].to_numpy())


from sklearn.neighbors import NearestNeighbors
neigh = NearestNeighbors(metric='cosine',algorithm='brute')
neigh.fit(prep_data)


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
transformer = FunctionTransformer(neigh.kneighbors,kw_args={'return_distance':False})
pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])

params={'n_neighbors':10,'return_distance':False}
pipeline.get_params()
pipeline.set_params(NN__kw_args=params)

pipeline.transform(extracted_data.iloc[0:1,6:15].to_numpy())[0]


def scaling(dataframe):
    scaler=StandardScaler()
    prep_data=scaler.fit_transform(dataframe.iloc[:,6:15].to_numpy())
    return prep_data,scaler

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh,scaler,params):
    transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
    pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
    return pipeline

def extract_data(dataframe,ingredient_filter,max_nutritional_values):
    extracted_data=dataframe.copy()
    for column,maximum in zip(extracted_data.columns[6:15],max_nutritional_values):
        extracted_data=extracted_data[extracted_data[column]<maximum]
    if ingredient_filter!=None:
        for ingredient in ingredient_filter:
            extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(ingredient,regex=False)]
    return extracted_data

def apply_pipeline(pipeline,_input,extracted_data):
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def recommand(dataframe,_input,max_nutritional_values,ingredient_filter=None,params={'return_distance':False}):
    extracted_data=extract_data(dataframe,ingredient_filter,max_nutritional_values)
    prep_data,scaler=scaling(extracted_data)
    neigh=nn_predictor(prep_data)
    pipeline=build_pipeline(neigh,scaler,params)
    return apply_pipeline(pipeline,_input,extracted_data)










# Home page
@app.route('/')
def home():
    return render_template('home.html')


# First Innings Score Prediction
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    temp_array = list()

    if request.method == 'POST':

        calories = float(request.form['calories'])
        fat_content = float(request.form['fatContent'])
        saturated_fat_content = float(request.form['saturatedFatContent'])
        cholesterol_content = float(request.form['cholesterolContent'])
        sodium_content = float(request.form['sodiumContent'])
        carbohydrate_content = float(request.form['carbohydrateContent'])
        fiber_content = float(request.form['fiberContent'])
        sugar_content = float(request.form['sugarContent'])
        protein_content = float(request.form['proteinContent'])
        test_input = np.array([[calories, fat_content, saturated_fat_content, cholesterol_content, sodium_content,
                         carbohydrate_content, fiber_content, sugar_content, protein_content]])
        print(test_input)

        x = recommand(dataset, test_input, max_list)
        print(x)

        return render_template('response.html', data=x)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
