-- Nfa.hs

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


-- This module implements some of the algorithms in Chapter 3 of
-- the book "Compilers: Principles, Techniques, & Tools", referred to
-- as the "Dragon book" through out the file
-- Specifically:
--   Converts a regular expression into a non-deterministic finite automaton (NFA)
--   Tests whether an NFA accepts a string
--   Converts an NFA into a deterministic finite automaton (DFA)
--   Tests whether a DFA accepts a string
--   Converts an NFA or DFA into a format that can be visualized with the GraphViz tool dot

module Nfa
    (fromRE, dfa_matches, nfa_matches, nfaToDot, dfaToDot, toDfa
    )
    --, minimize_dfa)
    where

import REParser

import qualified Data.Set as Set
import qualified Data.Map as Map

data NfaChar = NfaChar Char
             | Epsilon
               deriving (Eq, Ord)

-- Some types
type State = Int
type StateSet = Set.Set State
type DfaTransition = Map.Map State (Map.Map NfaChar State)
type NfaTransition = Map.Map State (Map.Map NfaChar (StateSet))

-- Nfa type definition
data Nfa = Nfa {
      -- The transition table
      n_transitions :: NfaTransition,

      -- The start state
      n_start :: Int,
      
      -- The set of accepting states
      n_accepting :: StateSet,

      -- The original regular expression
      n_rgx :: String
      } deriving (Show, Eq)

data Dfa = Dfa {
      -- The transition table
      d_transitions :: DfaTransition,

      -- The start state
      d_start :: Int,

      -- The set of accepting states
      d_accepting :: StateSet,

      -- The original regular expression
      d_rgx :: String
      } deriving (Show, Eq)

-- Epsilon -> &epsilon for dot output
instance Show NfaChar where
    show Epsilon = "&epsilon;"
    show (NfaChar a) = [a]


-- Given a state and a character, return the state the DFA transitions to
dfa_move :: State -> NfaChar -> Dfa -> State
dfa_move st ch fa = lookupDefault ch 0 (lookupDefault st Map.empty (d_transitions fa))

-- Create an empty NFA
empty :: String -> Nfa
empty re = (Nfa Map.empty 0 Set.empty re )

-- Convert a regular expression and ParseTree into an Nfa using the algorithm from
-- section 3.7.4 of the "Dragon book"
-- visit2 does all of the real work
visit :: String -> ParseTree -> Nfa
visit re pt =
    let
        -- Call visit2 to generate the transition table
        (lastState, nf) = (visit2 pt (0, (empty re)))
    in
      -- Construct the nfa
      nf {n_start = 0,
          n_accepting = (Set.insert lastState (n_accepting nf))
         }

-- Return the map of NfaChar -> StateSet for state st of Nfa fa
getCharMap :: State -> Nfa -> (Map.Map NfaChar (StateSet))
getCharMap st fa = lookupDefault st Map.empty (n_transitions fa)

-- Return the set of states that fa can transition to from state st on character ch
getTrans :: State -> NfaChar -> Nfa -> (StateSet)
getTrans st ch fa =
    let oldTrans = (n_transitions fa)
        innerMap = lookupDefault st Map.empty oldTrans
        goesTo = lookupDefault ch Set.empty innerMap
    in
      goesTo

-- Completely remove state st from Nfa fa
removeState :: State -> Nfa -> Nfa
removeState st fa =
    fa { n_transitions = newTrans }
    where
      -- Remove all states going to st from the transition table with st removed
      newTrans = (removeGoingTo st (Map.delete st (n_transitions fa)))

      -- Remove all states in cmgoing to st
      removeGoingTo st cm = Map.map (\x -> Map.map (\y -> Set.delete st y) x) cm

-- If key is in theMap return its value
-- Otherwise return def
lookupDefault :: (Ord a) => a -> b -> (Map.Map a b) -> b
lookupDefault key def theMap =
     case (Map.lookup key theMap) of
       Just x -> x
       Nothing -> def

-- Add a transition from st to ns on character ch
addTrans :: State -> NfaChar -> State -> Nfa -> Nfa
addTrans st ch ns fa =
    let oldTrans = (n_transitions fa)
        innerMap = lookupDefault st Map.empty oldTrans
        goesTo = lookupDefault ch Set.empty innerMap
    in
      let
          newGoesTo = Set.insert ns goesTo
          newInnerMap = Map.insert ch newGoesTo innerMap
          newTrans = Map.insert st newInnerMap oldTrans
      in
        fa { n_transitions = newTrans }

-- Add multiple new transitions to an Nfa
addMulti :: [(State, NfaChar, State)] -> Nfa -> Nfa
addMulti ((st, ch, ns):trs) fa = addTrans st ch ns (addMulti trs fa)
addMulti [] fa = fa

-- visit2 converts a ParseTree to an Nfa
-- cs is the current State counter, used for State ids
visit2 :: ParseTree -> (Int, Nfa) -> (Int, Nfa)

-- Do nothing on Empty
visit2 Empty (cs, fa) = (cs, fa)

-- For a character, add a transition from state cs to state (cs+1)
visit2 (Char v) (cs, fa) =
    (cs+1, (addTrans cs (NfaChar v) ((cs+1)::State) fa))

-- Concatenation links the last state of its left branch to the first state of its right branch 
visit2 (Concatenation l r) (cs, fa) = (visit2 r (visit2 l (cs, fa)))

-- Closure adds:
--    Its sub-tree's NFA
--    An e-transition skipping the sub-tree's NFA
--    An e-transition going to the first state of the sub-tree's NFA
--    An e-transition going from the sub-tree's last state to the sub-tree's first state
--    An e-transition going from the sub-tree's last state to the first state after the sub-tree's NFA
visit2 (Closure r) (cs, fa) =
    let
        fa1 = (addTrans cs Epsilon (cs+1) fa) -- e-transition to the sub-tree's NFA
        (cs2, fa2) = visit2 r (cs+1, fa1)
    in
      (cs2+1, addMulti [(cs2, Epsilon, cs2+1),  -- e-transition from last state in sub-tree's NFA to next state after sub-tree
                        (cs, Epsilon, cs2+1),   -- e-transition skipping sub-tree
                        (cs2, Epsilon, cs+1)] fa2) -- e-transition from last state in sub-tree's NFA to first state in sub-tree's NFA

-- Alternation addsL
--    NFA for each alternative
--    e-transitions going to each alternative
--    e-transitions going from each alternative to the first state after the alternation
visit2 (Alternation l r) (cs, fa) =
    let
        (cs2, fa2) = visit2 l (cs+1, (addTrans (cs) Epsilon (cs+1) fa)) -- Add left branch alternative
        (cs3, fa3) = visit2 r (cs2+1, (addTrans (cs) Epsilon (cs2+1) fa2))  -- Add right branch alternative
    in
      (cs3+1, addMulti [(cs3, Epsilon, cs3+1), (cs2, Epsilon, cs3+1)] fa3)  -- e-transitions to next state after the alternation

-- Convert a regex to an Nfa
fromRE :: String -> Nfa
fromRE re = --(visit re (parseRE re))
            (remove_epsilon_states (visit re (parseRE re)))

-- Create a string that can be fed into GraphViz's dot to display an Nfa
nfaToDot :: Nfa -> String
nfaToDot fa = let
--    keys = Map.keys (n_transitions fa)
    rv = "digraph G {\nlabel=\"" ++
         (n_rgx fa) ++ "\";\nrankdir = LR;\n"
                        ++ (concat rest)
                        ++ "node [shape=plaintext label=\"\"]; bob->0;\n"
                        ++ acceptCircles
                        ++ "}\n"
                           
        where
          rest = 
              (Map.foldWithKey
                      (\k x ac ->  
                           (Map.foldWithKey
                                   (\k2 y ad -> ad ++
                                                (Set.fold
                                                        (\sx sa -> sa ++ (show k)
                                                                   ++ "->" ++ (show sx)
                                                                   ++ " [label=\"" ++ (show k2) ++"\"];\n")
                                                        "" y))
                                   "" x) : ac)
               [] (n_transitions fa))

          acceptCircles = Set.fold
                          (\sx ac -> ac ++ (show sx) ++ " [shape=doublecircle]\n")
                          ""
                          (n_accepting fa)
    in
      rv

-- Create a string that can be fed into GraphViz's dot to display a Dfa
dfaToDot :: Dfa -> String
dfaToDot fa = let
--    keys = Map.keys (d_transitions fa)
    rv = "digraph G {\nlabel=\"" ++
         (d_rgx fa) ++ "\";\nrankdir = LR;\n"
                        ++ (concat rest)
                        ++ "node [shape=plaintext label=\"\"]; bob->0;\n"
                        ++ acceptCircles
                        ++ "}\n"
                           
        where
          rest = 
              (Map.foldWithKey
                      (\k x ac ->  
                           (Map.foldWithKey
                                   (\k2 y ad -> ad ++(show k) ++ "->" ++ (show y) ++ " [label=\"" ++ (show k2) ++"\"];\n")
                                   "" x) : ac)
               [] (d_transitions fa))

          acceptCircles = Set.fold
                          (\sx ac -> ac ++ (show sx) ++ " [shape=doublecircle]\n")
                          ""
                          (d_accepting fa)
    in
      rv

-- e_closure is described in Figure 3.31 of section 3.7.1 of the Dragon book
e_closure :: Nfa -> State -> (StateSet)
e_closure fa st =
    e_closure_set fa initial
    where initial = Set.insert st (getTrans st Epsilon fa)

-- e_closure_set is described in Figure 3.31 of section 3.7.1 of the Dragon book
e_closure_set :: Nfa -> (StateSet) -> (StateSet)
e_closure_set fa sts =
    e_closure_set_inner fa sts
    where e_closure_set_inner fa oldsts =
              let
                  tmp = Set.fold (\x acc -> Set.union (getTrans x Epsilon fa) acc) oldsts oldsts
              in
                if (tmp == oldsts)
                then oldsts
                else e_closure_set_inner fa tmp

-- nfa_move is described in Figure 3.31 of section 3.7.1 of the Dragon book
nfa_move :: Nfa -> (StateSet) -> NfaChar -> (StateSet)
nfa_move fa st ch = Set.fold (\x acc -> Set.union (getTrans x ch fa) acc) Set.empty st

-- Test whether an Nfa accepts for the given string
nfa_matches :: Nfa -> String -> Bool
nfa_matches fa str =
    ((Set.size (Set.intersection (n_accepting fa) (inner_match fa str (e_closure fa (n_start fa)))))>0)
    where
      inner_match fa ([]) set = set
      inner_match fa (x:xs) set = inner_match fa xs (e_closure_set fa (nfa_move fa set (NfaChar x)))

-- Test whether a Dfa accepts for the given string
dfa_matches :: Dfa -> String -> Bool
dfa_matches fa str =
    Set.member (inner_match fa str (d_start fa)) (d_accepting fa)
    where
      inner_match fa ([]) st = st
      inner_match fa (x:xs) st = (inner_match fa xs (dfa_move st (NfaChar x) fa))

-- Remove all "null" states from an Nfa
-- Just callls removeNullState for each state in the Nfa
remove_epsilon_states :: Nfa -> Nfa
remove_epsilon_states fa =
    rkeys fa (Map.keys (n_transitions fa))
    where
      rkeys fa ([]) = fa
      rkeys fa (x:xs) = removeNullState x (rkeys fa xs)

-- Checks if a state is null, if so removes it
removeNullState :: State -> Nfa -> Nfa
removeNullState st fa =
    -- Start state and accepting states can not be removed, null or not
    if ((st==0) || (Set.member st (n_accepting fa)))
    then fa
    else if ((Map.size cmap) /= 1) -- Accepting states can only leave on epsilon, so can only have one entry in cmap
         then fa
         else if (goesToOnEsp == Set.empty)  -- Make sure it only leaves on epsilon
              then fa
              else if ((Set.size comesFrom)==0) -- comesFrom is the things that go to st on epsilon
                   then fa
                   else eachToAll (removeState st fa) (Set.toList comesFrom) (Set.toList goesToOnEsp)
    where
      cmap = getCharMap st fa  -- st's transitions
      goesToOnEsp = getTrans st Epsilon fa -- st's epsilon transitions
      comesFrom = Set.fromList  -- Things with epsilon transitions to st
                  (Map.keys
                   (Map.filter
                           (\x -> Map.foldWithKey
                                  (\k y acc -> ((k==Epsilon && (Set.member st y)) || acc))
                                  False x
                           )
                           (n_transitions fa)
                   )
                  )

      -- Adds e-transitions from each state in (s:st) to every state in sts
      eachToAll f [] sts = f
      eachToAll f (s:st) sts  = eachToAll (goToAll f s sts) st sts

      -- Add e-transitions from st to every state in (s:ss)
      goToAll f st [] = f
      goToAll f st (s:ss) = goToAll (addTrans st Epsilon s f) st ss


-- Convert an Nfa to a Dfa using the algorithms from section 3.7.1 of the "Dragon book"
toDfa :: Nfa -> Dfa
toDfa nfa =
    let
        dstrt = e_closure nfa (n_start nfa)
        init = Map.fromList [(dstrt, genStates dstrt)]
        dfa = getps init
        stateNames = genStateMap dfa
        partial = Map.mapKeys (\x -> lookupDefault x 0 stateNames) dfa
        dfaTrans = Map.map (\x -> Map.map (\y -> (lookupDefault y 0 stateNames)) x) partial
        accepting = Set.fromList
                    (Map.elems
                            (Map.filterWithKey
                                    (\k x ->
                                         (Set.size (Set.intersection (n_accepting nfa) k)) > 0
                                    )
                             stateNames
                            )
                    )
    in
      Dfa dfaTrans (n_start nfa) accepting (n_rgx nfa)
    where
      getps old =
          if (new == old)
            then new
            else (getps new)
          where
            new = generateProductions old

      generateProductions :: Map.Map (StateSet) (Map.Map NfaChar (StateSet))
                          -> Map.Map (StateSet) (Map.Map NfaChar (StateSet))
      generateProductions fad = foldl
                                (\acc x ->
                                     let
                                         gt = (genStates x)
                                     in 
                                       Map.insert x gt acc
                                ) fad (getProductionStates fad) 

      genStateMap :: Map.Map (StateSet) (Map.Map NfaChar (StateSet))
                  -> Map.Map (StateSet) Int
      genStateMap dfa = foldl
                        (\acc x ->
                             let
                                 (y, sm) = mapState acc x
                             in
                               sm
                        ) Map.empty (Map.keys dfa)
      getProductionStates fad = (concat
                                 (map
                                  (\x -> Map.elems x)
                                  (Map.elems fad)
                                 )
                                )

      mapState sm set = case Map.lookup set sm of
                          Just y -> (y, sm)
                          Nothing -> let ms = Map.size sm
                                     in (ms, Map.insert set ms sm)
      genStates set = Map.fromList (filter (\(x,y) -> not (Set.null y))
                      (Set.toList
                              (Set.map
                                      (\ch -> (ch, e_closure_set nfa (nfa_move nfa set ch)))
                                      inSyms
                              )
                      ))
      inSyms = Set.delete Epsilon (Set.fromList (Map.fold (\x acc -> acc ++ Map.keys x) [] (n_transitions nfa)))

-- minimize_dfa :: Dfa -> ([NfaChar],Set.Set StateSet)
-- minimize_dfa dfa =
--       (symbols, Set.fromList (filter (\x -> x /= Set.empty) (partition initialPartition)))
--     where
--       non_accepting = (Set.difference (Set.fromList (Map.keys (d_transitions dfa))) (d_accepting dfa))
--       accepting = (d_accepting dfa)
--       initialPartition = [non_accepting, accepting]
--       symbols = Map.keys (head (Map.elems (d_transitions dfa)))
--       partition old =
--           if (new == old)
--             then new
--             else (partition new)
--           where
--             new = foldl (\acc x -> acc ++ (partList old x) ) initialPartition symbols

--       partList x y =
--           let
--               gt = (dfa_move (Set.findMin (head x)) y dfa)
--               (a,b) = Set.partition (\x -> (dfa_move x y dfa) == gt) (head x)
--           in
--             [a,b]
