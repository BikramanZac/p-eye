import subprocess
import collections

class ESpeak:
    def __init__(self, amplitude=100, word_gap=10, capitals=1, line_length=1,
                 pitch=50, speed=175, voice='en', spell_punctuation=[],
                 split=''):
        """
        The base ESpeak class. You can set espeak's arguments from the
        named parameters or change them after creation using the properties
        """

        args = [('amplitude',         ['-a', amplitude, int]),
                ('word_gap',          ['-g', word_gap, int]),
                ('capitals',          ['-k', capitals, int]),
                ('line_length',       ['-l', line_length, int]),
                ('pitch',             ['-p', pitch, int]),
                ('speed',             ['-s', speed, int]),
                ('voice',             ['-v', voice, str]),
                ('spell_punctuation', ['--punct=', ''.join(spell_punctuation),
                                       str]),
                ('split',             ['--split=', split, str])]
        self.args = collections.OrderedDict(args)
	
	
    def _espeak_args(self, text, filename=''):
        self._validate_args()
        if filename:
            save = ["{0}{1}".format(self.split[0], self.split[1]),
                    "-w{}".format(filename)]
        else:
            save = []
        args = ['espeak'] + \
               ["{0}{1}".format(v[0], v[1]) for v in self.args.values()] + \
               ['-x'] + save + [text]
        return args

    def _execute(self, cmd):
	subprocess.call(cmd)
	
    def say(self, text):
        """
        Make espeak read the text directly
        Parameters
        ----------
        text : str
            The text to be read
        Returns
        -------
        phoneme : str
            The phoneme, as read by speak
        """
        return self._execute(self._espeak_args(text))
    
    def _validate_args(self):
        for k, v in self.args.items():
            if type(v[1]) != v[2]:
                raise TypeError(
                    "Error: argument {0} does not match {1}".format(k, v[2]))
