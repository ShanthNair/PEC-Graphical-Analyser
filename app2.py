import os
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from flask import Flask, render_template, request

app2 = Flask(__name__)

def process_csv_files(dark_forward_file, light_forward_file, light_no_bias_file, light_reverse_file, forward_sr_file, reverse_sr_file):
    # Save the uploaded files temporarily
    dark_forward_path = 'temp/dark_forward.csv'
    light_forward_path = 'temp/light_forward.csv'
    light_no_bias_path = 'temp/light_no_bias.csv'
    light_reverse_path = 'temp/light_reverse.csv'
    forward_sr_path = 'temp/forward_sr.csv'
    reverse_sr_path = 'temp/reverse_sr.csv'
    dark_forward_file.save(dark_forward_path)
    light_forward_file.save(light_forward_path)
    light_no_bias_file.save(light_no_bias_path)
    light_reverse_file.save(light_reverse_path)
    forward_sr_file.save(forward_sr_path)
    reverse_sr_file.save(reverse_sr_path)

    # Read CSV files and convert columns to float within a single DataFrame
    df_dark_forward = pd.read_csv(dark_forward_path)
    df_light_forward = pd.read_csv(light_forward_path)
    df_light_no_bias = pd.read_csv(light_no_bias_path)
    df_light_reverse = pd.read_csv(light_reverse_path)
    df_light_forward_sr = pd.read_csv(forward_sr_path)
    df_light_reverse_sr = pd.read_csv(reverse_sr_path)

    # Delete the temporary files
    os.remove(dark_forward_path)
    os.remove(light_forward_path)
    os.remove(light_no_bias_path)
    os.remove(light_reverse_path)
    os.remove(forward_sr_path)
    os.remove(reverse_sr_path)

    # Convert necessary columns to float
    df_list = [df_dark_forward, df_light_forward, df_light_no_bias, df_light_reverse, df_light_forward_sr, df_light_reverse_sr]
    columns_to_convert = ['voltage across solar cell', 'current', 'Log(Voltage)', 'Log(Current)']
    for df in df_list:
        df[columns_to_convert] = df[columns_to_convert].astype(float)

    return df_dark_forward, df_light_forward, df_light_no_bias, df_light_reverse, df_light_forward_sr, df_light_reverse_sr

def create_matplotlib_figure(df_dark_forward, df_light_forward, df_light_no_bias, df_light_reverse, df_light_forward_sr, df_light_reverse_sr):
    # Create a Matplotlib figure
    figure = Figure(figsize=(6, 4), dpi=100)
    plot1 = figure.add_subplot(221)
    plot2 = figure.add_subplot(222)
    plot3 = figure.add_subplot(223)
    plot4 = figure.add_subplot(224)

    # Plot 1: Forward & Reverse Bias Plots for both Light & Dark Experimental Conditions
    plot1.plot(df_dark_forward["voltage across solar cell"].values, df_dark_forward["current"].values, linestyle='dotted', label="Dark-Forward")
    plot1.plot(df_light_forward["voltage across solar cell"].values, df_light_forward["current"].values, linestyle='dotted', label="Light-Forward")
    plot1.plot(df_light_no_bias["voltage across solar cell"].values, df_light_no_bias["current"].values, linestyle='dotted', label="Light-No Bias")
    plot1.plot(df_light_reverse["voltage across solar cell"].values, df_light_reverse["current"].values, linestyle='dotted', label="Light-Reverse")
    plot1.set_title("Forward & Reverse Bias Plots")
    plot1.set_xlabel("Voltage Across Solar Cell (V)")
    plot1.set_ylabel("Current (A)")
    plot1.legend()

    # Plot 2: Ln(Current) vs. Ln(Voltage) for Light-Forward Bias Experimental Conditions
    plot2.plot(df_light_forward["Log(Voltage)"].values, df_light_forward["Log(Current)"].values, linestyle='dotted')
    plot2.set_title("Ln(Current) vs. Ln(Voltage) for Light-Forward Bias")
    plot2.set_xlabel("Ln(Voltage)")
    plot2.set_ylabel("Ln(Current)")

    # Plot 3: Current vs. Voltage to find Series Resistance using Forward-Light Conditions
    plot3.plot(df_light_forward_sr["voltage across solar cell"].values, df_light_forward_sr["current"].values, linestyle='dotted')
    plot3.set_title("Current vs. Voltage (Series Resistance)")
    plot3.set_xlabel("Voltage across solar cell(V)")
    plot3.set_ylabel("Current(A)")

    # Plot 4: Current vs. Voltage to find Shunt Resistance using Reverse-Light Conditions
    plot4.plot(df_light_reverse_sr["voltage across solar cell"].values, df_light_reverse_sr["current"].values, linestyle='dotted')
    plot4.set_title("Current vs. Voltage (Shunt Resistance)")
    plot4.set_xlabel("Voltage across solar cell(V)")
    plot4.set_ylabel("Current(A)")

    return figure

@app2.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded CSV files
        dark_forward_file = request.files['dark_forward']
        light_forward_file = request.files['light_forward']
        light_no_bias_file = request.files['light_no_bias']
        light_reverse_file = request.files['light_reverse']
        forward_sr_file = request.files['forward_sr']
        reverse_sr_file = request.files['reverse_sr']

        # Process the uploaded CSV files
        df_dark_forward, df_light_forward, df_light_no_bias, df_light_reverse, df_light_forward_sr, df_light_reverse_sr = process_csv_files(
            dark_forward_file, light_forward_file, light_no_bias_file, light_reverse_file, forward_sr_file, reverse_sr_file
        )

        # Create a Matplotlib figure
        figure = create_matplotlib_figure(
            df_dark_forward, df_light_forward, df_light_no_bias, df_light_reverse, df_light_forward_sr, df_light_reverse_sr
        )

        # Create the FigureCanvasTkAgg object to display the Matplotlib figure in the Flask app2
        canvas = FigureCanvasTkAgg(figure, master=app2)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Convert the Matplotlib figure to Plotly JSON representation
        figure_json = figure.to_json()

        return render_template('index.html', figure_json=figure_json)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app2.run(debug=True)