import ollama


def llm_call_up(name,age, position, team, results):
    prompt = f"""
    I need you to create a scouting report on  {name}
    Can you provide me with a summary of their strengths and weaknesses?

    Here is the data I have on him:

    Player: {name}
    Position: {position}
    Age: {age}
    Team: {team}

    Some stats averaged per 90 minutes and the percentiles are described here {results.to_markdown()}

    Return the scouting report in the following markdown format:

    # Scouting Report for {name}

    ## Summary    
    < a brief summary of the player's overall performance and if he would be beneficial to the team >

    ## Strengths
    < a list of 1 to 3 strengths >

    ## Weaknesses
    < a list of 0 to 3 weaknesses >

    """
    print(ollama.list())
    ollama.pull('llama3')
    results = ollama.chat(model="tinyllama",messages=[{"role":"user","content":prompt,
                                           }])
    response = results["message"]["content"]

    return response

