# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- The game looked like a simple web game where it randomly generated a number and we as the user had to guess what it was. The color scheme of gray and blue helped makes the web game look nice and the UI was also pleasant to look at, but I feel like the user should be prompted with what the difficulty should be first because it kinda blends in with the gray color.
- List at least two concrete bugs you noticed at the start  
- First bug: The hints were backwards, lets say the random number was 50, if we guessed 20 it would say we should go lower and not go higher.
- Second bug: initial allowed attempts and attempts left are not correct. the initial allowed attempts says 8 while the attempts left is 7 when you first boot up the game.
- Third bug: When shown the developer debug menu, the button seems to be unresponsive when you first attempt to press, but works just fine on the second press.
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input             | Expected Behavior            | Actual Behavior                     | Console Output / Error                          |
|-------------------|------------------------------|-------------------------------------|-------------------------------------------------|
| Guess of 50       | Too high                     | Too low                             | Printed out "Too low"                           |
| Guessed any #     | History showing latest input | Input is Delayed till next button   | None                                            |
| New Game          | Starts a new game            | Does nothing if you guess correctly | You already won. Start a new game to play again.|
| New Game          | Starts a new game            | on running out of attempts          | Game over. Start a new game to try again.       |
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? 
  I used Gemini
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  I asked gemini what was the intended implementation for update score and what should be changed so that the score matches up to what it is intended to do. This is what the AI suggested the correct implementation was as well as the bugs it found:
  
  The bugs in the current version

def update_score(current_score, outcome, attempt_number):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)   # Bug A: off-by-one
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5               # Bug B: rewards a wrong guess
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
Bug A — off-by-one on the win bonus. attempt_number is already incremented before this is called (line 148), so it's the count including the current attempt. Adding + 1 again double-penalizes. Winning on the 1st attempt gives 100 - 10*(1+1) = 80 instead of the intended 100 - 10*1 = 90 (or 100 if you don't want to charge for the winning guess at all).

Bug B — "Too High" sometimes adds points. On even attempts a too-high guess gives +5. A wrong guess should never increase the score, and the two wrong outcomes are handled inconsistently — "Too Low" always loses 5, "Too High" sometimes gains 5. Both should be treated the same.

Correct implementation

def update_score(current_score, outcome, attempt_number):
    if outcome == "Win":
         points = 100 - (10 * (attempt_number - 1))   # first-try win = 100, slower = less
        if points < 10:
            points = 10                      # floor so a late win still scores
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5             # any wrong guess: same small penalty

    return current_score                     # parse errors etc.: no change

After running the game again and doing a few guesses on what the random number was that it generated, it did guess correctly that the one off error did in fact exist and returned a score that was higher than the previous and now the scoring system now works properly..



- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

One AI suggestion that was incorrect or misleading was the score resetting itself. On every new reset after fixing the reset bug, the counter accumulates the previous runs scores and just adds it to the current total. The AI after initially scanning it thinks that it resets itself after each and every reset. This was the hint that it suggested:

  Resetting score = 0 on New Game vs. a running total
  If your design intends score to accumulate across games, the New Game reset to 0 wipes it. If it's per-game, this is correct. Decide which — right now the win/loss messages say "Final score," implying per-game, so 0 is probably right.



---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  I decided whether or not a bug was really fixed after doing a few trial runs and testing out, and then using the test.py file that claude generated and then I reread to make sure that it uses the correct diffculty, format, etc.

- Describe at least one test you ran (manual or using pytest).  
  ran the test.py that claude generated and verified that the results that it got was what the webpage/app was returning after running streamlit.

- Did AI help you design or understand any tests? How?
  Yes, the AI did help me design all of the tests because I did not know how I would configure or setup the streamlit portions of the test. Thankfully from what I have seen it did it pretty well in checking each function within the app.py file and most of it runs correctly.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  Streamlit is essentially an all-in-one solution in building a simple website with no hassle of dealing with HTML or CSS. In particular detail in how we can use streamlit functions such as reruns is very simple, reruns essentially just refreshes the page without having to actually fresh it from the browser itself. It is very helpful in restarting a method or applicaiton such as getting a new game to start. 

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  Instead of just outright asking it to build a pytest method in order to help build my skillset into building my own, I would ask it what functions should I really need to make sure runs on first attempt prior to checking if everything else works first. i would also try to give it a bit more context and improve my prompting strategies to make sure that it fully understands what it needs to do in the current context.
- What is one thing you would do differently next time you work with AI on a coding task?
  I would definitely not ask it to write an entire test.py file since it would definitely use methods I am not familiar with or is not pratical at all.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
  It was definitely much more accurate then I would give it credit for, it definitely understood what the problem was and solved it a good 90% of the time without me even giving it a direction. I had to mislead it a tiny bit by being very vague.
