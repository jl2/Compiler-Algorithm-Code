test: Main.hs Nfa.hs REParser.hs
	ghc -O2 -o test --make Main.hs Nfa.hs REParser.hs
	strip test

.PHONY:
	clean

clean:
	rm -f *.hi *.o
