from flask import Flask, redirect, render_template, url_for, request, jsonify, session
import os
import random
import sqlite3

flashcard_applet = Flask(__name__)
flashcard_applet.secret_key = os.urandom(24)  # Set a secret key for session management

# For db name 'russian_flashcards.db'
def get_db_connection():
    # Use the absolute path to the database file
    conn = sqlite3.connect(r'C:\Users\trett\Documents\UWYO\Russian2024\FlashcardApp\russian_flashcards.db')
    return conn

# Define the allowed word types
ALLOWED_WORD_TYPES = {'nouns', 'verbs', 'adjectives'}

# Define the cases
CASES = {
    'acc': 'кого/что', 
    'gen': 'кого/чего', 
    'dat': 'кому/чему', 
    'inst': 'кем/чем', 
    'prep': 'о ком/о чем'
}

@flashcard_applet.route('/random_word/<word_type>')
def random_word(word_type):
    if word_type not in ALLOWED_WORD_TYPES:
        return redirect(url_for('index'))

    random_word, translations = get_random_word(word_type)
    return render_template('flashcard.html', word=random_word, translations=translations)

def get_random_word(word_type='nouns'):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    word_details = None
    translations = None

    # Try fetching a word with translations up to 1000 times
    for _ in range(1000):
        cur.execute(f'SELECT * FROM {word_type} LIMIT 1000')
        words = cur.fetchall()
        random_word = random.choice(words)

        word_id = random_word['word_id']
        cur.execute('SELECT _form_bare FROM words_forms WHERE word_id = ?', (word_id,))
        word_details = cur.fetchone()
        cur.execute('SELECT tl FROM translations WHERE word_id = ?', (word_id,))
        translations = cur.fetchall()

        if word_details and translations:
            break  # Exit the loop if a valid word with translations is found

    conn.close()

    return dict(word_details), [dict(translation) for translation in translations]

@flashcard_applet.route('/')
def index():
    # This is your main page or default route
    return render_template('index.html')

@flashcard_applet.route('/get_new_word')
def get_new_word():
    difficulty = request.args.get('difficulty', default='beginner')
    noun, adj, case_ch, interrogative, noun_form, adj_form, is_plural, noun_gender = get_case_practice_data(difficulty)
    return jsonify({
        'noun': noun,
        'adj': adj,
        'case_ch': case_ch,
        'interrogative': interrogative,
        'noun_form': noun_form,
        'adj_form': adj_form,
        'is_plural': is_plural,
        'noun_gender': noun_gender
    })

@flashcard_applet.route('/flashcard')
def flashcard():

    default_word_type = 'nouns'
    word_details, translations = get_random_word(default_word_type)
    return render_template('flashcard.html', word=word_details, translations=translations)

@flashcard_applet.route('/case_practice')
def case_practice():
    difficulty = request.args.get('difficulty', default='beginner')
    word_data = get_case_practice_data(difficulty)  # This now returns a dictionary

    return render_template('case_practice.html', difficulty=difficulty, **word_data)

@flashcard_applet.route('/get_word')
def get_word():
    difficulty = request.args.get('difficulty', 'beginner')
    direction = request.args.get('direction', 'next')

    # Check if 'current_word' is not in session or initialize it
    if 'current_word' not in session:
        initial_word_data = get_case_practice_data('beginner')  # Assuming 'beginner' as default difficulty
        session['current_word'] = initial_word_data

    if direction == 'next':
        if 'next_word' in session:
            # If moving forward after going back, use the stored 'next_word'
            new_word_data = session['next_word']
        else:
            # Otherwise, fetch a new word and update session
            new_word_data = get_case_practice_data(difficulty)
            session['previous_word'] = session.get('current_word', {})
            session['current_word'] = new_word_data
        # Clear 'next_word' since we're moving forward
        session.pop('next_word', None)
    elif direction == 'previous':
        # Use the 'previous_word' if available; otherwise, do nothing (new_word_data remains None)
        new_word_data = session.get('previous_word')
        if new_word_data:
            # Prepare for potential forward navigation by saving the current word as 'next_word'
            session['next_word'] = session.get('current_word', {})
            # Update 'current_word' to reflect the backward move
            session['current_word'] = new_word_data

    return jsonify(new_word_data if new_word_data else {})

def get_case_practice_data(difficulty='beginner'):

    # Define limits for each difficulty
    limits = {'beginner': 100, 'intermediate': 500, 'advanced': 2000, 'native': 10000}
    limit = limits.get(difficulty, 150)  # Default to 150 if difficulty not found

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    for attempt in range(10):  # Attempt up to 10 times to find a valid word
        # Randomly select a case
        case_ch = random.choice(list(CASES.keys()))
        interrogative = CASES[case_ch]

        # Randomly decide if plural (25% chance)
        is_plural = random.random() < 0.25

        # Fetch the top X nouns and randomly select one
        if limit is not None:
            cur.execute('SELECT * FROM nouns LIMIT ?', (limit,))
        else:
            cur.execute('SELECT * FROM nouns')
        nouns = cur.fetchall()
        noun_row = random.choice(nouns)
        cur.execute('SELECT tl FROM translations WHERE word_id = ? AND position = 1', (noun_row['word_id'],))
        noun_translation_row = cur.fetchone()
        if not noun_translation_row:
            continue
        
        noun_translation = noun_translation_row['tl'].split(', ')[:1]
        noun = ", ".join(noun_translation).replace(' noun', '')  # Remove ' noun' from the noun
        noun_id = noun_row['word_id']
        noun_gender = noun_row['gender']

        # Fetch the correct form for the noun
        noun_form_tag = f'ru_noun_{"pl" if is_plural else "sg"}_{case_ch}'
        cur.execute('SELECT form FROM words_forms WHERE word_id = ? AND form_type = ?', (noun_id, noun_form_tag))
        noun_form_row = cur.fetchone()
        if not noun_form_row:
            continue
        
        noun_form = noun_form_row['form']

        # Fetch the top X adjectives and randomly select one
        if limit is not None:
            cur.execute('SELECT * FROM adjectives LIMIT ?', (limit,))
        else:
            cur.execute('SELECT * FROM adjectives')
        adjectives = cur.fetchall()
        adj_row = random.choice(adjectives)
        cur.execute('SELECT tl FROM translations WHERE word_id = ? AND position = 1', (adj_row['word_id'],))
        adj_translation_row = cur.fetchone()
        if not adj_translation_row:
            continue

        adj_translation = adj_translation_row['tl'].split(', ')[:1]
        adj = ", ".join(adj_translation).replace(' adj', '')  # Remove ' adj' from the adjective
        adj_id = adj_row['word_id']

        # Fetch the correct form for the adjective
        adj_form_tag = f'ru_adj_{"pl" if is_plural else noun_gender}_{case_ch}'
        cur.execute('SELECT form FROM words_forms WHERE word_id = ? AND form_type = ?', (adj_id, adj_form_tag))
        adj_form_row = cur.fetchone()
        if not adj_form_row:
            continue

        adj_form = adj_form_row['form']

        if noun_form_row and adj_form_row:
            # Construct and return a dictionary directly
            return {
                'noun': noun,
                'adj': adj,
                'case_ch': case_ch,
                'interrogative': interrogative,
                'noun_form': noun_form,
                'adj_form': adj_form,
                'is_plural': is_plural,
                'noun_gender': noun_gender
            }

    else:  # If no valid word found after 10 attempts, return a dictionary indicating failure
        return {
        'noun': "Not Found",
        'adj': "Not Found",
        'case_ch': "Not Found",
        'interrogative': "Not Found",
        'noun_form': "Not Found",
        'adj_form': "Not Found",
        'is_plural': False,
        'noun_gender': "Not Found"
        }
    conn.close()


if __name__ == '__main__':
    flashcard_applet.run(debug=True)


    