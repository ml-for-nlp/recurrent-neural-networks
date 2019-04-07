# The amazing RNN cats tutorial

In this tutorial, you will be using a slightly modified version of [Andrej Karpathy's RNN code](https://gist.github.com/karpathy/d4dee566867f8291f086) to do character-based language modeling.

Typical language modeling examples involve generating Shakespeare. It is often difficult to judge the quality of the output (unless you're a Shakespeare buff). So let's think of something else we can generate in a character-based fashion...

ASCII cats.

```
      /\_/\
 /\  / o o \
//\\ \~(*)~/
`  \/   ^ /
   | \|| ||
   \ '|| ||
    \)()-())
```

(This  fine example is taken from [this awesome page](http://www.asciiworld.com/-Cats-.html).)

## The data

You have tiny data to play with, contained in the cat.txt file. The file basically contains the ASCII cat shown above.

## Running the RNN cats

Let's first run the program. It needs various parameters, in this form:

    python3 cat-char-rnn.py cat.txt --seq_length=20 --hidden_size=200 --num_epochs=100 --lr=0.01

If you run this, the RNN will try and learn how to draw the cat from the data in cat.txt, and attempt to regenerate it. With the above parameters, here is what the output might look like:

```
EPOCH 90
----
   \\  /~ || /\\  ) /|\  | o \~ /\~ \
 /|    /
_ \~ /|    ' |/|~ | ^ o   |

||
 \   |  ||  \~o/\~/\
  
----
iter 360, loss: 45.598756
----
```

OK. This looks more like a splatter movie than a cat. Your job is to recover the cat by setting the network parameters right, and doing whatever else might be needed.


## Help! My cat does not have paws!

Look at your input data again. Imagine you're the RNN, with the current hyperparameters you are using. What happens when you get to the cat's paws in the data? Can you see what you would have to do to fix the problem?

## Memorising the cat

One way to reproduce the cat perfectly would be to fully memorise the drawing. This is not very interesting from the point of view of building a network that will generalise, but it is a good exercise to think about how this could be made to happen. How would you go about it? Do you have to change anything in the code itself? (Check how it samples the cat!) Is it possible?

## Embrace your evil scientist side

Let's now see how well the RNN actually generalises. We'll expand our data with ascii-modified cats. For instance, three-eyed cats and whisker-less cats (creepy!):

```
      /\_/\
 /\  / ooo \
//\\ \~(*)~/
`  \/   ^ /
   | \|| ||
   \ '|| ||
    \)()-())

      /\_/\
 /\  / o o \
//\\ \ (*) /
`  \/   ^ /
   | \|| ||
   \ '|| ||
    \)()-())
```

How is sampling impacted? Can you experiment further with different types of cats? (Be creative!) What happens with different sequence lengths? When do things break? 

## Expand your zoo

The [ASCII art page](http://www.asciiworld.com/) has lots more animals on offer. Go and pick some, and see which ones your RNN will be able to model and which not. Can you explain its behaviour?
