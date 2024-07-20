import plotly as plo
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pickle
from flask import Flask, request

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from sklearn.preprocessing import scale
import warnings
warnings.filterwarnings('ignore')


app = Flask(__name__)
datadeveloped = pd.read_csv('developedcountryfinal.csv')
datadeveloping = pd.read_csv('developingcountryfinal.csv')
alldata = pd.read_csv('Alldata.csv')

with open('developingmodel.pkl', 'rb') as file:
    modeldeveloping = pickle.load(file)

with open('developedmodel.pkl', 'rb') as file:
    modeldeveloped = pickle.load(file)

#this is endpoint to get list of all countries 
@app.route('/countries', methods=['GET'])
def getCountries():
    # print("developed Countries", datadeveloped["Country"].unique())
    # print("develping Countries", datadeveloping["Country"].unique())
    devlopingCon = datadeveloping["Country"].unique()
    developedCon = datadeveloped["Country"].unique()
    countries = devlopingCon.tolist() + developedCon.tolist()
    output = []

    #make a list of countries with its status 
    for country in countries:
        country_row = alldata.loc[alldata['Country'] == country].iloc[0]
        country_status = country_row['Status']
        output.append({"name": country, "status": country_status})
    return output

# this is endpoint which called to predict and send plots to front end
@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.get_json()
    print("input_data", input_data)
    countryname = input_data["countryname"]
    inputs = {}
    if "inputs" in input_data:
        inputs = input_data["inputs"]

 #  this module does the prediction of life expextancy for developed country . This is redirected once the user chooses a country
    def developingCountry(countryname, inputs):

        #default values of input
        Adult_Mortality = 263.0
        HIV_AIDS = 0.1
        GDP = 543.77
        five_deaths = 83
        Income_resources = 0.479
        Schooling = 10.1

        #assiging input values to the variables 
        if inputs:
            if 'Adult_Mortality' in inputs:
                Adult_Mortality = inputs["Adult_Mortality"]

            if 'HIV_AIDS' in inputs:
                HIV_AIDS = inputs["HIV_AIDS"]

            if 'GDP' in inputs:
                GDP = inputs["GDP"]

            if 'five_deaths' in inputs:
                five_deaths = inputs["five_deaths"]

            if 'Income_resources' in inputs:
                Income_resources = inputs["Income_resources"]

            if 'Schooling' in inputs:
                Schooling = inputs["Schooling"]

        # testinput takes the input combination provided by the user and goes inside the predicted model to estimate life expectancy 
        testinput = np.array(
            [Adult_Mortality, HIV_AIDS, GDP, five_deaths, Income_resources, Schooling])
        test = testinput.reshape(1, testinput.shape[0])
        predict = modeldeveloping.predict(test)
        countrydata = datadeveloping.loc[datadeveloping['Country']
                                         == countryname]
        print(predict)

        columns_list = countrydata.columns

        fig = make_subplots(rows=2, cols=3)
        # This loop is used to plot the life expectecy with respect with the input features
        for i, d in enumerate(columns_list[3:]):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.add_trace(
                go.Scatter(
                    x=countrydata[d],
                    y=countrydata["Life_expectancy"],
                    mode='markers',
                    marker=dict(
                        color='blue',
                        opacity=0.9,
                        size=8,
                        line=dict(width=0.5, color='white')
                    ),
                    name=d
                ),
                row=row, col=col
            )
            fig.add_trace(
                go.Scatter(
                    x=[testinput[i]],
                    y=[predict[0]],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=8
                    ),
                    name='Your Chosen Point',
                    showlegend=False,
                    hovertemplate='(%{x}, %{y})<br><b>Your chosen point</b>'),
                row=row, col=col
            )

            fig.update_xaxes(title_text=d, row=row, col=col)
            fig.update_yaxes(title_text='Life Expectancy', row=row, col=col)

        fig.update_layout(
            title={
                'text': f"Predicted Life Expectancy of {countryname} is {round(predict[0],2)} years <br> {countryname} is a developing country \n ",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        # fig.show()
        # This section shows the life expectancy variation with respect to variation of the input provided the user.
        # we vary +- 20% stepwise variation on top the data provided by the user to show additional feedback
        input_names = ['Adult Mortality', 'HIV/AIDS', 'GDP',
                       '5 year deaths', 'Income resources', 'Schooling']

        # Define subplot layout
        fig2 = make_subplots(rows=2, cols=3, subplot_titles=input_names)

        # Define function to generate bar plot
        def plot_impact(input_name, input_value, row, col):
            # Loop through different input values
            x = ['-20%', '-10%', '0%', '+10%', '+20%']
            y = []
            for value in [0.8, 0.9, 1.0, 1.1, 1.2]:
                # Update the input value for the current input parameter
                new_input = test.copy()
                new_input[0, input_names.index(input_name)] *= value

                # Predict with the model and store the result
                prediction = modeldeveloping.predict(new_input)
                y.append(prediction[0])

            # Add bar plot to subplot
            fig2.add_trace(go.Bar(x=x, y=y), row=row, col=col)
            fig2.update_xaxes(
                title_text=f'{input_name} ({input_value})', row=row, col=col)
            fig2.update_yaxes(title_text='Life Expectancy', row=row, col=col)

        # Generate bar plot for each input feature
        for i, (input_name, input_value) in enumerate(zip(input_names, testinput)):
            plot_impact(input_name, input_value, row=i//3+1, col=i % 3+1)

        # Update subplot layout
        fig2.update_layout(
            title=f'Impact of changing input features on Life Expectancy in {countryname}')
        # fig2.show()
        # my_bar_chart = py.plot(fig, include_plotlyjs=False, output_type='div')
        graphJSON = plo.io.to_json(fig, pretty=True)
        graphJSON2 = plo.io.to_json(fig2, pretty=True)
        return {"fig1": graphJSON, "fig2": graphJSON2}

# This module does the prediction of life expextancy for developed country . This is redirected once the user chooses a country
    def developedCountry(countryname, inputs):
        #default values of input
        Adult_Mortality = 6
        percentage_expenditure = 1400
        thinness_1_19_years = 0.6
        thinness_5_9_years = 0.6
        Income_resources = 0.936
        Schooling = 20.4

        #assiging input values to the variables
        if inputs:
            if 'Adult_Mortality' in inputs:
                Adult_Mortality = inputs["Adult_Mortality"]

            if 'percentage_expenditure' in inputs:
                percentage_expenditure = inputs["percentage_expenditure"]

            if 'thinness_1_19_years' in inputs:
                thinness_1_19_years = inputs["thinness_1_19_years"]

            if 'x' in inputs:
                thinness_5_9_years = inputs["thinness_5_9_years"]

            if 'Income_resources' in inputs:
                Income_resources = inputs["Income_resources"]

            if 'Schooling' in inputs:
                Schooling = inputs["Schooling"]

        # testinput takes the input combination provided by the user and goes inside the predicted model to estimate life expectancy 
        testinput = np.array([Adult_Mortality, percentage_expenditure,
                             thinness_1_19_years, thinness_5_9_years, Income_resources, Schooling])
        test = testinput.reshape(1, testinput.shape[0])
        predict = modeldeveloped.predict(test)
        countrydata = datadeveloped.loc[datadeveloped['Country']
                                        == countryname]
        print(predict)

        columns_list = countrydata.columns

        fig = make_subplots(rows=2, cols=3)

        # This loop is used to plot the life expectecy with respect with the input features
        for i, d in enumerate(columns_list[3:]):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.add_trace(
                go.Scatter(
                    x=countrydata[d],
                    y=countrydata["Life_expectancy"],
                    mode='markers',
                    marker=dict(
                        color='blue',
                        opacity=0.9,
                        size=8,
                        line=dict(width=0.5, color='white')
                    ),
                    name=d
                ),
                row=row, col=col
            )
            fig.add_trace(
                go.Scatter(
                    x=[testinput[i]],
                    y=[predict[0]],
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=8
                    ),
                    name='Your Chosen Point',
                    showlegend=False,
                    hovertemplate='(%{x}, %{y})<br><b>Your chosen point</b>'),
                row=row, col=col
            )

            fig.update_xaxes(title_text=d, row=row, col=col)
            fig.update_yaxes(title_text='Life Expectancy', row=row, col=col)

        fig.update_layout(
            title={
                'text': f"Predicted Life Expectancy of {countryname} is {round(predict[0],2)} years <br> {countryname} is a developed country \n ",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        # fig.show()
        # This section shows the life expectancy variation with respect to variation of the input provided the user.
        # we vary +- 20% stepwise variation on top the data provided by the user to show additional feedback
        input_names = ['Adult Mortality', 'percentage_expenditure',
                       'thinness_1_19_years', 'thinness_5_9_years', 'Income resources', 'Schooling']

        # Define subplot layout
        fig2 = make_subplots(rows=2, cols=3, subplot_titles=input_names)

        # Define function to generate bar plot
        def plot_impact(input_name, input_value, row, col):
            # Loop through different input values
            x = ['-20%', '-10%', '0%', '+10%', '+20%']
            y = []
            for value in [0.8, 0.9, 1.0, 1.1, 1.2]:
                # Update the input value for the current input parameter
                new_input = test.copy()
                new_input[0, input_names.index(input_name)] *= value

                # Predict with the model and store the result
                prediction = modeldeveloped.predict(new_input)
                y.append(prediction[0])

            # Add bar plot to subplot
            fig2.add_trace(go.Bar(x=x, y=y), row=row, col=col)
            fig2.update_xaxes(
                title_text=f'{input_name} ({input_value})', row=row, col=col)
            fig2.update_yaxes(title_text='Life Expectancy', row=row, col=col)

        # Generate bar plot for each input feature
        for i, (input_name, input_value) in enumerate(zip(input_names, testinput)):
            plot_impact(input_name, input_value, row=i//3+1, col=i % 3+1)

        # Update subplot layout
        fig2.update_layout(
            title=f'Impact of changing input features on Life Expectancy in {countryname}')
        # fig2.show()
        graphJSON = plo.io.to_json(fig, pretty=True)
        graphJSON2 = plo.io.to_json(fig2, pretty=True)
        return {"fig1": graphJSON, "fig2": graphJSON2}
    # countryname = 'Austria'

    # getting row associate with countryname
    india_row = alldata.loc[alldata['Country'] == countryname].iloc[0]
    #getting contry status (developing or developed)
    country_status = india_row['Status']

    if country_status == 'Developing':
        html = developingCountry(countryname, inputs)
    else:
        html = developedCountry(countryname, inputs)

    return html


if __name__ == '__main__':
    app.run(debug=True)

    Adult_Mortality = 263.0
    HIV_AIDS = 0.1
    GDP = 543.77
    five_deaths = 83
    Income_resources = 0.479
    Schooling = 10.1

    testinput = np.array([Adult_Mortality, HIV_AIDS, GDP,
                         five_deaths, Income_resources, Schooling])
    test = testinput.reshape(1, testinput.shape[0])
    predict = modeldeveloping.predict(test)
    countrydata = datadeveloping.loc[datadeveloping['Country'] == countryname]
    print(predict)

    columns_list = countrydata.columns

    fig = make_subplots(rows=2, cols=3)

    for i, d in enumerate(columns_list[3:]):
        row = (i // 3) + 1
        col = (i % 3) + 1
        fig.add_trace(
            go.Scatter(
                x=countrydata[d],
                y=countrydata["Life_expectancy"],
                mode='markers',
                marker=dict(
                    color='blue',
                    opacity=0.9,
                    size=8,
                    line=dict(width=0.5, color='white')
                ),
                name=d
            ),
            row=row, col=col
        )
        fig.add_trace(
            go.Scatter(
                x=[testinput[i]],
                y=[predict[0]],
                mode='markers',
                marker=dict(
                    color='red',
                    size=8
                ),
                name='Your Chosen Point',
                showlegend=False,
                hovertemplate='(%{x}, %{y})<br><b>Your chosen point</b>'),
            row=row, col=col
        )

        fig.update_xaxes(title_text=d, row=row, col=col)
        fig.update_yaxes(title_text='Life Expectancy', row=row, col=col)

    fig.update_layout(
        title={
            'text': f"Predicted Life Expectancy is {predict[0]} <br>Life Expectancy of {countryname} \n ",
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    fig.show()

    input_names = ['Adult Mortality', 'HIV/AIDS', 'GDP',
                   '5 year deaths', 'Income resources', 'Schooling']

    # Define subplot layout
    fig = make_subplots(rows=2, cols=3, subplot_titles=input_names)

    # Define function to generate bar plot
    def plot_impact(input_name, input_value, row, col):
        # Loop through different input values
        x = ['-20%', '-10%', '0%', '+10%', '+20%']
        y = []
        for value in [0.8, 0.9, 1.0, 1.1, 1.2]:
            # Update the input value for the current input parameter
            new_input = test.copy()
            new_input[0, input_names.index(input_name)] *= value

            # Predict with the model and store the result
            prediction = modeldeveloping.predict(new_input)
            y.append(prediction[0])

        # Add bar plot to subplot
        fig.add_trace(go.Bar(x=x, y=y), row=row, col=col)
        fig.update_xaxes(
            title_text=f'{input_name} ({input_value})', row=row, col=col)
        fig.update_yaxes(title_text='Life Expectancy', row=row, col=col)

    # Generate bar plot for each input feature
    for i, (input_name, input_value) in enumerate(zip(input_names, testinput)):
        plot_impact(input_name, input_value, row=i//3+1, col=i % 3+1)

    # Update subplot layout
    fig.update_layout(
        title=f'Impact of changing input features on Life Expectancy in {countryname}')
    fig.show()
