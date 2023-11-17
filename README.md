# DrDictaphone

```
$ python cli-process.py --context context/proofread-de.yaml --input test/text-garbage.txt
Error: [ ... ]

$ python cli-process.py --context context/proofread-de.yaml --input test/text-de.txt
Das ist ein Beispieltext in deutscher Sprache, der ein paar relativ einfache Fehler enthält. ChatGPT sollte ohne weiteres in der Lage sein, diese Fehler zu korrigieren.

$ python cli-dictate.py --context context/transcribe-de.yaml --input some_audio.wav --output test-output.txt

$ python cli-dictate.py --context context/transcribe-de.yaml --output test-output.txt
starting recorder
[ ... ]

```
