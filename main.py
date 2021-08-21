import random as r
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objs as go
from math import ceil

# Preliminary account details
_START_PITY = 53
_GACHA_RATE = .994
_SOFT_PITY_RATE = .666
_NEXT_5_STAR_50_50 = True
_CURRENCY_PER_SINGLE_PULL = 160

# Randomizing threshold calculations
_NORMAL_PITY_THRESHOLD = _GACHA_RATE * 1000
_SOFT_PITY_THRESHOLD = _SOFT_PITY_RATE * 1000

# Sample size to consider
_NUM_TRIALS = 1000

def getPullCurrencyValue(currency: int = _CURRENCY_PER_SINGLE_PULL, average: float = 0) -> int:
    """
    Calculates the number of gacha currency is needed to (on average) get that desired character
    """
    return ceil(average) * currency

def getBestCaseList(result_list: list) -> int:
    """
    Returns the best case simulated result from the many num trials
    """
    return min(result_list)

def getWorstCaseList(result_list: list) -> int:
    """
    Returns the worst case simulated result from the many num trials
    """
    return max(result_list)

def getAverageList(result_list: list) -> float:
    """
    Returns the average case simulated result from the many num trials
    """
    return sum(result_list) / len(result_list)

def generateRandNum() -> int:
    """
    Generates a random number from 1 to 1000, inclusive to the endpoints, used to simulate the probability
    """
    return r.randint(1, 1000)

def normalPityRate() -> bool:
    """
    Checks to see if the 'summon' was successful for normal pity rate
    """
    return generateRandNum() > _NORMAL_PITY_THRESHOLD

def softPityRate() -> bool:
    """
    Checks to see if the 'summon' was successful for soft pity rate
    """
    return generateRandNum() > _SOFT_PITY_THRESHOLD

def wonFiftyFiftyRate() -> bool:
    """
    Uses the randomly generated number to see if simulated result wins the 50-50
    """
    return generateRandNum() >= 500

def getCorrectCharacter() -> bool:
    """
    Function to describe the Mihoyo guaranteed rate up unit pity system.
    If you lose the 50-50 for the 5* character, then the next one will be
    guaranteed to be that 5* character. If you get that specific 5* character,
    then the next 5* you obtain will be a 50-50 chance
    """
    global _NEXT_5_STAR_50_50
    if _NEXT_5_STAR_50_50 and wonFiftyFiftyRate():
        _NEXT_5_STAR_50_50 = True
        return True
    elif _NEXT_5_STAR_50_50 and not wonFiftyFiftyRate():
        _NEXT_5_STAR_50_50 = False
        return False
    elif not _NEXT_5_STAR_50_50:
        _NEXT_5_STAR_50_50 = True
        return True

if __name__ == "__main__":
    # list storage for simulated results
    total_pity_count_list = []
    extra_summons_list = []

    # Sweep through the number of trials
    for i in range(0, _NUM_TRIALS):
        count = _START_PITY
        prev_count = 0
        
        while True:
            count += 1
            # Soft pity starts at 76 summons in
            if count <= 75:
                got5Star = normalPityRate()
            # Hard pity is at 90
            elif count < 90:
                got5Star = softPityRate()
            else:
                got5Star = True

            if got5Star and getCorrectCharacter():
                if count + prev_count > _START_PITY:
                    total_pity_count_list.append(count)
                    if prev_count > 0:
                        total_pity_count_list.append(prev_count)
                    extra_summons_list.append(count + prev_count - _START_PITY)
                break
            elif got5Star:
                prev_count = count
                count = 0

    # Print out results in the terminal
    print(f"Average Pity Count: {getAverageList(total_pity_count_list)}")
    print(f"Average Extra Summons: {getAverageList(extra_summons_list)}, or {getPullCurrencyValue(_CURRENCY_PER_SINGLE_PULL, getAverageList(extra_summons_list))} primogems")
    print(f"Average Worst Case Extra Summons: {getWorstCaseList(extra_summons_list)}, or {getPullCurrencyValue(_CURRENCY_PER_SINGLE_PULL, getWorstCaseList(extra_summons_list))} primogems")
    print(f"Average Best Case Extra Summons: {getBestCaseList(extra_summons_list)}, or {getPullCurrencyValue(_CURRENCY_PER_SINGLE_PULL, getBestCaseList(extra_summons_list))} primogems")

    # Generate a distribution plot of the results
    distplot_label = ['Simulated Extra Summons']
    fig = ff.create_distplot([extra_summons_list], distplot_label)
    fig.update_layout(
        title_text='Amount to Summon to Get Character',
        xaxis_title='Num Summons'
    )
    fig.show()

    # Generate a CDF plot of the distributions
    # Referenced: https://stackoverflow.com/questions/65402296/python-plotly-cdf-with-frequency-distribution-data
    hist, bin_edges = np.histogram(extra_summons_list, bins=(getWorstCaseList(extra_summons_list) - getBestCaseList(extra_summons_list)), density=True)
    cdf = np.cumsum(hist * np.diff(bin_edges))
    fig2 = go.Figure(data=[
        go.Scatter(x=bin_edges, y=cdf, name='Cumulative Probability of Summons')
    ])
    fig2.update_layout(
        title_text='Cumulative Probability to Get Character',
        xaxis_title='Num Summons',
        yaxis_title='Probability'
    )
    fig2.show()