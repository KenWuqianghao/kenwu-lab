"""Word lists copied from the authors' notebook Rise_fall_rationality_analysis_Figs.ipynb (cells 6, 8)."""
SCIENCE = ['science', 'technology', 'scientific', 'chemistry', 'chemicals', 'physics', 'medicine',
           'uncertainty', 'model', 'methodology', 'method', 'fact', 'data', 'hypothesis', 'statistics',
           'math', 'analysis', 'conclusion', 'replication', 'limit', 'result', 'determine', 'transmission',
           'assuming', 'system']
QUANT = ['size', 'unit', 'pressure', 'area', 'density', 'percent']
BELIEF = ['spirit', 'imagine', 'wisdom', 'wise', 'hunch', 'mind', 'suspicion', 'believe', 'think',
          'trust', 'faith', 'truth', 'true', 'belief', 'doubt', 'hope', 'fear', 'life', 'soul',
          'heaven', 'eternal', 'mortal', 'holy', 'god', 'pray', 'mystery']
SENSES = ['sense', 'sensation', 'feel', 'soft', 'hard', 'cold', 'hot', 'smell', 'foul', 'taste',
          'sweet', 'bitter', 'hear', 'sound', 'silence', 'loud', 'see', 'gaze', 'glimpse', 'light',
          'dark', 'bright']
A_ALL = SCIENCE + QUANT          # rationality
B_ALL = BELIEF + SENSES          # intuition

# Words of A_ALL / B_ALL that are in the authors' 5000-word list (most_frequent_words.pkl, 'eng').
# Missing from A: uncertainty, methodology, hypothesis, statistics, replication, density.
# Missing from B: sensation, gaze, glimpse.  (checked by analysis.py when the repo is present)
NOT_IN_5000 = {'uncertainty', 'methodology', 'hypothesis', 'statistics', 'replication', 'density',
               'sensation', 'gaze', 'glimpse'}
A = [w for w in A_ALL if w not in NOT_IN_5000]
B = [w for w in B_ALL if w not in NOT_IN_5000]
assert len(A) == 25 and len(B) == 45
