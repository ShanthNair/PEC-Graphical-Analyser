from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

app = Flask(__name__)

mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

def plot_data(df, label):
    plt.plot(df["voltage across solar cell"].values, df["current"].values, linestyle='dotted', label=label)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if all five required files are present
        files = ['file1', 'file2', 'file3', 'file4', 'file6']  # Exclude shunt resistance file (file5)
        for file in files:
            if file not in request.files:
                return "Please upload all required files"
        
        # Process each file and create plots
        plot_labels = ['Light - Forward', 'Light - Reverse', 'Dark - Forward', 'Dark - Reverse', 'Light - No Bias']
        plt.figure(figsize=(10, 6))
        for i, label in enumerate(plot_labels, start=1):
            file = request.files[f'file{i}']
            if file.filename == '':
                return f"No selected file for File {i}"
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)
            
            # Process the DataFrame (type conversion, etc.)
            df['voltage across solar cell'] = df['voltage across solar cell'].astype(float)
            df['current'] = df['current'].astype(float)
            
            # Plot the data
            plot_data(df, label)
        
        # Customize the plot
        plt.xlabel("Voltage Across Solar Cell (V)")
        plt.ylabel("Current (A)")
        plt.title("Solar Cell Data - Forward & Reverse Bias Plots")
        plt.legend()
        plt.grid(True)
        
        # Save the plot as a PNG image
        plt.savefig('static/compiled_plot.png')  # Save the plot as compiled_plot.png in the static folder
        plt.clf()  # Clear the current figure
        
        # Instead of rendering the template, redirect to the new page
        return redirect('/plot')
    
    return render_template('index.html')

@app.route('/plot')
def plot_page():
    plot_url = '/static/compiled_plot.png'
    return render_template('plots.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
