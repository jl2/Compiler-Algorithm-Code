-- Main.hs

-- Copyright (c) 2010, Jeremiah LaRocco jeremiah.larocco@gmail.com

-- Permission to use, copy, modify, and/or distribute this software for any
-- purpose with or without fee is hereby granted, provided that the above
-- copyright notice and this permission notice appear in all copies.

-- THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
-- WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
-- MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
-- ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
-- WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
-- ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
-- OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.



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

