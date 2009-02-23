


module Main () where

import Nfa
import System.Environment (getArgs)
    
main = do
  args <- System.Environment.getArgs
  case args of
    [] -> putStrLn "No argument given."
    _ -> let
           a1 = (head args)
           jim = fromRE a1
           tom = toDfa jim
      in
        putStrLn (dfaToDot tom)
        -- if (dfa_matches tom (head (tail args))) then
--             putStrLn ("DFA Matches\n" ++ (if (nfa_matches jim (head (tail args))) then "NFA Matches" else "NFA does not match") ++ (dfaToDot tom)   ++ (nfaToDot jim))

--         else
--             putStrLn ("DFA does not match\n" ++ (if (nfa_matches jim (head (tail args))) then "NFA Matches" else "NFA does not match") ++ (dfaToDot tom)  ++ (nfaToDot jim))

