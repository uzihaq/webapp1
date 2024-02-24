from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import os
import zipfile
import random

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'

def try_read_csv(file_stream, encodings=('utf-8', 'ISO-8859-1', 'windows-1252')):
    for encoding in encodings:
        try:
            file_stream.seek(0)  # Reset file stream to the beginning
            return pd.read_csv(file_stream, encoding=encoding), None
        except UnicodeDecodeError:
            continue
    return None, "Failed to read the file with provided encodings."

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['quizFile']
        if file and file.filename:
            num_questions = int(request.form.get('numQuestions', 1))
            num_quizzes = int(request.form.get('numQuizzes', 1))
            
            df, error = try_read_csv(file)
            if error:
                flash(error)
                return redirect(url_for('index'))
            
            generate_quizzes(df, num_questions, num_quizzes)
            return send_file('quizzes.zip', as_attachment=True, download_name='Quizzes.zip')
        else:
            flash('No file selected.')
            return redirect(url_for('index'))

    return render_template('index.html')

def generate_quizzes(df, num_questions, num_quizzes):
    if not os.path.exists('quizzes'):
        os.makedirs('quizzes')
        
    for quizNum in range(num_quizzes):
        quiz_file_path = f'quizzes/Quiz_{quizNum + 1}.txt'
        answer_key_file_path = f'quizzes/Quiz_answers_{quizNum + 1}.txt'
        
        with open(quiz_file_path, 'w') as quizFile, open(answer_key_file_path, 'w') as answerKeyFile:
            selected_questions = df.sample(n=min(num_questions, len(df))).reset_index(drop=True)
            for questionNum, row in selected_questions.iterrows():
                question, answer = row[0], row[1]
                quizFile.write(f'{questionNum + 1}. {question}\n')
                answerKeyFile.write(f'{questionNum + 1}. {answer}\n')
                quizFile.write('\n')
    
    # ZIP the quizzes
    with zipfile.ZipFile('Quizzes.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk('quizzes'):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

if __name__ == '__main__':
    app.run(debug=True)
