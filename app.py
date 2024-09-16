from flask import Flask, request, render_template
from ml_dependencies import predict_text_from_user

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the text input from the user
        text = request.form['news_input']
        
        # Use the ML SVC model to make a prediction
        prediction = "True" if predict_text_from_user(text) else "False"
        
        # Render the page with the prediction
        return render_template('index.html', prediction=prediction, text=text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
