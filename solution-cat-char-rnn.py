"""
Minimal character-level Vanilla RNN model. Written by Andrej Karpathy (@karpathy)
Modified by Aurelie Herbelot.
BSD License

Usage:
    min-char-rnn.py <input_file> --seq_length=NUM --hidden_size=NUM --num_epochs=NUM --lr=<lr>

Options:
    -h --help     Show this screen.
"""



import numpy as np
from docopt import docopt
from nltk import edit_distance
import sys


def lossFun(inputs, targets, hprev, Wxh, Whh, Why, bh, by):
  """
  inputs,targets are both list of integers.
  hprev is Hx1 array of initial hidden state
  returns the loss, gradients on model parameters, and last hidden state
  """
  xs, hs, ys, ps = {}, {}, {}, {}
  hs[-1] = np.copy(hprev)
  loss = 0
  # forward pass
  for t in range(len(inputs)):
    xs[t] = np.zeros((vocab_size,1)) # encode in 1-of-k representation
    xs[t][inputs[t]] = 1
    hs[t] = np.tanh(np.dot(Wxh, xs[t]) + np.dot(Whh, hs[t-1]) + bh) # hidden state
    ys[t] = np.dot(Why, hs[t]) + by # unnormalized log probabilities for next chars
    ps[t] = np.exp(ys[t]) / np.sum(np.exp(ys[t])) # probabilities for next chars - softmax
    loss += -np.log(ps[t][targets[t],0]) # softmax (cross-entropy loss)
  # backward pass: compute gradients going backwards
  dWxh, dWhh, dWhy = np.zeros_like(Wxh), np.zeros_like(Whh), np.zeros_like(Why) #gradient matrices have same shape as weight matrices
  dbh, dby = np.zeros_like(bh), np.zeros_like(by)
  dhnext = np.zeros_like(hs[0])
  for t in reversed(range(len(inputs))):
    dy = np.copy(ps[t])
    dy[targets[t]] -= 1 # backprop into y. see http://cs231n.github.io/neural-networks-case-study/#grad if confused here
    dWhy += np.dot(dy, hs[t].T)
    dby += dy
    dh = np.dot(Why.T, dy) + dhnext # backprop into h
    dhraw = (1 - hs[t] * hs[t]) * dh # backprop through tanh nonlinearity
    dbh += dhraw
    dWxh += np.dot(dhraw, xs[t].T)
    dWhh += np.dot(dhraw, hs[t-1].T)
    dhnext = np.dot(Whh.T, dhraw)
  for dparam in [dWxh, dWhh, dWhy, dbh, dby]:
    np.clip(dparam, -5, 5, out=dparam) # clip to mitigate exploding gradients
  return loss, dWxh, dWhh, dWhy, dbh, dby, hs[len(inputs)-1]

def sample(h, seed_ix, n, Wxh, Whh, Why, bh, by):
  """ 
  sample a sequence of integers from the model 
  h is memory state, seed_ix is seed letter for first time step
  """
  x = np.zeros((vocab_size, 1))
  x[seed_ix] = 1 #for the one-hot vector
  ixes = []
  for t in range(n):
    h = np.tanh(np.dot(Wxh, x) + np.dot(Whh, h) + bh)
    y = np.dot(Why, h) + by
    p = np.exp(y) / np.sum(np.exp(y)) #softmax
    #ix = np.random.choice(range(vocab_size), p=p.ravel())  #sampling from distribution with higher probability to pick chars with high ps
    ix = p.ravel().argmax()
    x = np.zeros((vocab_size, 1))
    x[ix] = 1
    ixes.append(ix)
  return ixes

def train(hidden_size):
    # model parameters
    Wxh = np.random.randn(hidden_size, vocab_size)*0.01 # input to hidden
    Whh = np.random.randn(hidden_size, hidden_size)*0.01 # hidden to hidden
    Why = np.random.randn(vocab_size, hidden_size)*0.01 # hidden to output
    bh = np.zeros((hidden_size, 1)) # hidden bias
    by = np.zeros((vocab_size, 1)) # output bias

    n, p = 0, 0
    mWxh, mWhh, mWhy = np.zeros_like(Wxh), np.zeros_like(Whh), np.zeros_like(Why)
    mbh, mby = np.zeros_like(bh), np.zeros_like(by) # memory variables for Adagrad
    smooth_loss = -np.log(1.0/vocab_size)*seq_length # loss at iteration 0 -- give some equal loss to all labels

    best_score = 100
    epoch_count = 0
    while epoch_count < num_epochs:
      # prepare inputs (we're sweeping from left to right in steps seq_length long)
      if p+seq_length+1 >= len(data) or n == 0: 
        hprev = np.zeros((hidden_size,1)) # reset RNN memory
        p = 0 # go from start of data
        # sample from the model
        if epoch_count > 0 and epoch_count % 10 == 0:
            print("EPOCH",epoch_count)
            sample_ix = sample(hprev, inputs[0], 100, Wxh, Whh, Why, bh, by) #100 chars is a little more than the size of the original cat
            txt = ''.join(ix_to_char[ix] for ix in sample_ix)
            score = edit_distance(data,txt)
            if score < best_score:
                best_score = score
            print('----\n %s \n----' % (txt, ))
            print('iter %d, loss: %f, score: %f' % (n, smooth_loss, score)) # print progress
            print('----\n')
        epoch_count+=1
      inputs = [char_to_ix[ch] for ch in data[p:p+seq_length]]
      targets = [char_to_ix[ch] for ch in data[p+1:p+seq_length+1]]
      #print("X:",''.join([ix_to_char[i] for i in inputs]))
      #print("T:",''.join([ix_to_char[i] for i in targets]))

      # forward seq_length characters through the net and fetch gradient
      #print(hprev)
      loss, dWxh, dWhh, dWhy, dbh, dby, hprev = lossFun(inputs, targets, hprev, Wxh, Whh, Why, bh, by)
      #Label smoothing so that network does not become overconfident 
      #add some uniform loss to the actual loss
      smooth_loss = smooth_loss * 0.999 + loss * 0.001 
      
      # perform parameter update with Adagrad
      for param, dparam, mem in zip([Wxh, Whh, Why, bh, by], 
                                    [dWxh, dWhh, dWhy, dbh, dby], 
                                    [mWxh, mWhh, mWhy, mbh, mby]):
        mem += dparam * dparam
        param += -learning_rate * dparam / np.sqrt(mem + 1e-8) # adagrad update

      p += seq_length # move data pointer
      n += 1 # iteration counter 

    return best_score

def optimize():
    best_score = 100
    best_hyperparams = ""
    for hidden_size in range(50,200,50):
        print("--- hidden:",hidden_size)
        score = train(hidden_size)
        if score < best_score:
            best_score = score
            best_hyperparams = 'hidden: %d' % (hidden_size)
    print(best_score,best_hyperparams)


if __name__ == '__main__':
    args = docopt(__doc__, version='The amazing cat RNN tutorial 0.1')
    print(args)
    input_file = args["<input_file>"]
    data = open(input_file, 'r').read() # should be simple plain text file
    chars = list(set(data))
    data_size, vocab_size = len(data), len(chars)
    print('data has %d characters, %d unique.' % (data_size, vocab_size))
    char_to_ix = { ch:i for i,ch in enumerate(chars) }
    ix_to_char = { i:ch for i,ch in enumerate(chars) }

    # hyperparameters
    hidden_size = int(args["--hidden_size"])    # size of hidden layer of neurons
    seq_length = int(args["--seq_length"])      # number of steps to unroll the RNN for
    num_epochs = int(args["--num_epochs"])      # number of steps to unroll the RNN for
    learning_rate = float(args["--lr"])
    
    #optimize()
    train(hidden_size)
