import os
import sys
import random
from mainconnect import game
from tabulate import tabulate
import copy

# Ensure scores directory exists
dir_path = os.path.join(os.getcwd(), "scores")
os.makedirs(dir_path, exist_ok=True)

# Clean scores folder before starting
for f in os.listdir(dir_path):
    os.remove(os.path.join(dir_path, f))

teams = ['dc', 'csk', 'rcb', 'mi', 'kkr', 'pbks', 'rr', 'srh']
points = {}
battingInfo = {}
bowlingInfo = {}

# Initialize points table
for team in teams:
    points[team] = {
        "P": 0, "W": 0, "L": 0, "T": 0,
        "runsScored": 0, "ballsFaced": 0,
        "runsConceded": 0, "ballsBowled": 0,
        "pts": 0
    }

battingf = 0
bowlingf = 0

# Enhanced commentary lines for different events
commentary_lines = {
    'start': [
        "It's a packed stadium today, folks! The atmosphere is electric!",
        "The players are ready, and the crowd is roaring for action!",
        "What a perfect day for some thrilling cricket!"
    ],
    '0': [
        "Good ball! Dot ball, no run scored.",
        "Tight bowling, the batsman defends solidly.",
        "No run, excellent line and length from the bowler!"
    ],
    '1': [
        "Quick single taken, good running between the wickets!",
        "Pushed for a single, smart cricket.",
        "One run added to the total, tidy shot."
    ],
    '2': [
        "Nicely placed for a couple of runs!",
        "Two runs, good placement in the gap.",
        "Driven for two, excellent running!"
    ],
    '3': [
        "Three runs! Brilliant effort in the field to stop the boundary.",
        "Rare three runs, well-judged by the batsmen.",
        "Three to the total, superb running!"
    ],
    '4': [
        "FOUR! Cracked through the covers, what a shot!",
        "Boundary! Perfectly timed, races to the fence.",
        "FOUR runs! That’s a glorious cover drive!"
    ],
    '6': [
        "SIX! Launched over the stands, what a hit!",
        "Huge SIX! That’s gone miles into the crowd!",
        "Maximum! Smashed with authority!"
    ],
    'wicket': {
        'caught': [
            "Caught! Edged and taken!",
            "Caught! Simple catch for the fielder.",
            "Caught! What a grab! That was flying!",
            "Caught! The batsman walks, a good take in the field."
        ],
        'bowled': [
            "Bowled him! Right through the gate!",
            "Bowled! Timber! The stumps are a mess!",
            "Bowled! Cleaned him up, no answer to that delivery!"
        ],
        'lbw': [
            "LBW! That looked plumb! The umpire raises the finger.",
            "LBW! Trapped in front, that's got to be out!",
            "LBW! He's given him. Looked like it was hitting the stumps."
        ],
        'runOut': [ # Note: 'runout' (lowercase 'o') is used in mainconnect logs for out_type
            "Run out! Terrible mix-up, and he's short of his ground!",
            "Run out! Direct hit! What a piece of fielding!",
            "Run out! They went for a risky single, and paid the price."
        ],
        'stumped': [
            "Stumped! Quick work by the keeper, he was out of his crease!",
            "Stumped! Fooled by the flight, and the bails are off in a flash.",
            "Stumped! Great take and stumping by the wicketkeeper."
        ],
        'hitwicket': [
            "Hit wicket! Oh dear, he's knocked his own bails off!",
            "Hit wicket! What a bizarre way to get out!",
            "Hit wicket! He's dislodged the bails with his bat/body."
        ],
        'general': [ # Fallback for any other wicket type or if specific type not found
            "OUT! That's a big wicket for the bowling side!",
            "WICKET! The batsman has to depart.",
            "GONE! A crucial breakthrough for the bowlers."
        ]
    },
    'wide': [
        "Wide ball! The bowler strays down the leg side.",
        "Called wide, too far outside off stump.",
        "Extra run! Wide from the bowler."
    ],
    'end': [
        "What a match that was, folks! A true spectacle!",
        "The crowd is buzzing after that thrilling finish!",
        "A game to remember for years to come!"
    ],
    'innings_end': [
        "That’s the end of the innings. A solid total on the board!",
        "Innings wrapped up, setting up an exciting chase!",
        "End of the batting effort, now over to the bowlers!"
    ],
    'no_ball_call': [
        "No Ball! The bowler has overstepped. Free hit coming up!",
        "That's a No Ball! An extra run and a free hit.",
        "No Ball called by the umpire. The next delivery is a free hit."
    ],
    'free_hit_delivery': [ # Can be appended or used standalone
        "Free Hit delivery!",
        "Here comes the Free Hit...",
        "Batsman has a free license on this Free Hit!"
    ],
    'no_ball_runs': [ # For runs scored off a no-ball delivery
        "And runs scored off the No Ball! Adding insult to injury.",
        "They pick up runs on the No Ball as well!",
        "The batsman cashes in on the No Ball delivery!"
    ],
    'extras': { # New category for Byes and Leg-byes
        'B': [
            "Byes signalled! They sneak a single as the keeper misses.",
            "That's byes, well run by the batsmen.",
            "A bye taken as the ball evades everyone."
        ],
        'LB': [
            "Leg Byes! Off the pads and they run.",
            "Signalled as Leg Byes by the umpire.",
            "They get leg-byes for that deflection."
        ]
    }
}

def display_points_table():
    pointsTabulate = []
    for team in points:
        data = points[team]
        nrr = 0
        if data['ballsFaced'] > 0 and data['ballsBowled'] > 0:
            nrr = (data['runsScored'] / data['ballsFaced']) * 6 - (data['runsConceded'] / data['ballsBowled']) * 6
        row = [team.upper(), data['P'], data['W'], data['L'], data['T'], round(nrr, 2), data['pts']]
        pointsTabulate.append(row)
    pointsTabulate = sorted(pointsTabulate, key=lambda x: (x[6], x[5]), reverse=True)
    print("\nCurrent Points Table:")
    print(tabulate(pointsTabulate, headers=["Team", "Played", "Won", "Lost", "Tied", "NRR", "Points"], tablefmt="grid"))

def display_top_players():
    battingTabulate = []
    for b in battingInfo:
        c = battingInfo[b]
        outs = sum(1 for bl in c['ballLog'] if "W" in bl)
        avg = round(c['runs'] / outs, 2) if outs else float('inf')
        sr = round((c['runs'] / c['balls']) * 100, 2) if c['balls'] else 0
        battingTabulate.append([b, c['runs'], avg, sr])
    battingTabulate = sorted(battingTabulate, key=lambda x: x[1], reverse=True)[:3]
    
    print("\nTop 3 Batsmen:")
    print(tabulate(battingTabulate, headers=["Player", "Runs", "Average", "Strike Rate"], tablefmt="grid"))

    bowlingTabulate = []
    for b in bowlingInfo:
        c = bowlingInfo[b]
        economy = round((c['runs'] / c['balls']) * 6, 2) if c['balls'] else float('inf')
        bowlingTabulate.append([b, c['wickets'], economy])
    bowlingTabulate = sorted(bowlingTabulate, key=lambda x: x[1], reverse=True)[:3]
    
    print("\nTop 3 Bowlers:")
    print(tabulate(bowlingTabulate, headers=["Player", "Wickets", "Economy"], tablefmt="grid"))

def display_scorecard(bat_tracker, bowl_tracker, team_name, innings_num):
    print(f"\n--- {team_name.upper()} Scorecard: Innings {innings_num} ---")
    
    # Batting Scorecard
    batsmanTabulate = []
    for player in bat_tracker:
        data = bat_tracker[player]
        runs = data['runs']
        balls = data['balls']
        sr = round((runs / balls) * 100, 2) if balls else 'NA'
        how_out = "DNB"
        batted = False
        for log in data['ballLog']:
            batted = True
            if "W" in log:
                if "CaughtBy" in log:
                    split_log = log.split("-")
                    catcher = split_log[2]
                    bowler = split_log[-1]
                    how_out = f"c {catcher} b {bowler}"
                elif "runout" in log:
                    how_out = "Run out"
                else:
                    split_log = log.split("-")
                    out_type = split_log[1]
                    bowler = split_log[-1]
                    how_out = f"{out_type} b {bowler}"
            else:
                how_out = "Not out" if balls > 0 else "DNB"
        if batted or balls > 0:
            batsmanTabulate.append([player, runs, balls, sr, how_out])
    
    print("\nBatting:")
    print(tabulate(batsmanTabulate, headers=["Player", "Runs", "Balls", "SR", "How Out"], tablefmt="grid"))

    # Bowling Scorecard
    bowlerTabulate = []
    for player in bowl_tracker:
        data = bowl_tracker[player]
        runs_conceded = data['runs'] # Renamed for clarity from mainconnect.py 'runs'
        balls_bowled = data['balls']
        wickets_taken = data['wickets']
        noballs_bowled = data.get('noballs', 0) # Get noballs, default to 0 if not present
        overs_str = f"{balls_bowled // 6}.{balls_bowled % 6}" if balls_bowled else "0.0"
        economy_rate = round((runs_conceded / balls_bowled) * 6, 2) if balls_bowled else 'NA'
        bowlerTabulate.append([player, overs_str, runs_conceded, wickets_taken, noballs_bowled, economy_rate])
    
    print("\nBowling:")
    print(tabulate(bowlerTabulate, headers=["Player", "Overs", "Runs", "Wickets", "NB", "Economy"], tablefmt="grid"))

def display_ball_by_ball(innings_log, innings_num, team_name, runs, balls, wickets, bat_tracker, bowl_tracker):
    print(f"\n--- Innings {innings_num}: {team_name} Batting ---")

    i = 0
    while i < len(innings_log):
        event_data = innings_log[i]
        event_text = event_data['event']
        commentary = ""

        event_type = event_data.get('type')
        original_event_type = event_data.get('original_event_type')
        is_fh_delivery = event_data.get('is_free_hit_delivery', False)
        extras_type = event_data.get('extras_type')
        # Use runs_this_ball from event_data, not the function parameter 'runs' which is total innings runs
        runs_this_ball_current_event = event_data.get('runs_this_ball', 0)

        consolidated_nb_commentary = False
        no_ball_suffix = random.choice(commentary_lines['no_ball_call']).split('.')[1].strip() # "Free hit coming up!"

        if event_type == "NO_BALL_CALL":
            total_nb_runs = 1 # Start with the penalty run

            if i + 1 < len(innings_log):
                next_event_data = innings_log[i+1]
                if next_event_data.get('original_event_type') == "NB" and next_event_data.get('is_free_hit_delivery'):
                    runs_off_nb_delivery = next_event_data.get('runs_this_ball', 0)
                    total_nb_runs += runs_off_nb_delivery

                    event_text = next_event_data['event'] # Use event text from the ball outcome for score accuracy
                    commentary = f"Nb ({total_nb_runs})! {no_ball_suffix}"

                    i += 1 # Skip the next log entry as it's processed
                    consolidated_nb_commentary = True

            if not consolidated_nb_commentary: # Fallback if lookahead failed
                commentary = f"Nb (1)! {no_ball_suffix}"

        elif event_type == "WIDE":
            commentary = random.choice(commentary_lines['wide'])
        elif event_type == "EXTRAS" and extras_type in commentary_lines['extras']:
            runs_off_extras = event_data.get('runs_off_extras', 0) # This specific key might be from an older version of log
            # Assuming 'runs_this_ball' now holds extras runs for 'EXTRAS' type events
            # If 'runs_off_extras' is not reliably in the log, use runs_this_ball_current_event for extras amount
            actual_extras_runs = event_data.get('runs_off_extras', runs_this_ball_current_event)

            base_commentary = random.choice(commentary_lines['extras'][extras_type])
            if actual_extras_runs > 0:
                 base_commentary += f" {actual_extras_runs} run{'s' if actual_extras_runs > 1 else ''}."
            commentary = base_commentary
        else: # Handles legal deliveries, and outcomes of No-Balls if not consolidated
            out_type = event_data.get('out_type')
            is_not_out_on_fh = event_data.get('is_dismissal') == False and is_fh_delivery

            base_commentary = ""
            outcome_runs_str = ""

            if out_type and not is_not_out_on_fh: # Actual wicket dismissal
                if out_type in commentary_lines['wicket']:
                    base_commentary = random.choice(commentary_lines['wicket'][out_type])
                else:
                     base_commentary = random.choice(commentary_lines['wicket']['general']) + f" ({out_type})"
            elif is_not_out_on_fh:
                outcome_runs_str = str(runs_this_ball_current_event)
                run_commentary = random.choice(commentary_lines.get(outcome_runs_str, commentary_lines['0']))
                base_commentary = f"Phew! {run_commentary} (Not out on Free Hit!)"
            else: # Runs or dot
                outcome_runs_str = str(runs_this_ball_current_event)
                base_commentary = random.choice(commentary_lines.get(outcome_runs_str, commentary_lines['0']))

            if is_fh_delivery and not consolidated_nb_commentary :
                commentary = random.choice(commentary_lines['free_hit_delivery']) + " " + base_commentary
            else:
                commentary = base_commentary

        print(f"Ball {event_data.get('balls', 'N/A')}: {event_text} - {commentary}")
        i += 1 # Move to next log item

    overs = f"{balls // 6}.{balls % 6}"
    print(f"\nInnings Total: {runs}/{wickets} in {overs} overs")
    print(random.choice(commentary_lines['innings_end']))
    
    # Display scorecard after innings
    display_scorecard(bat_tracker, bowl_tracker, team_name, innings_num)

# League Matches Scheduling (Round Robin)
def generate_round_robin_schedule(team_list_input):
    """
    Generates a round-robin schedule where each team plays every other team once.
    Uses the circle method. Ensures original list is not modified.
    """
    local_teams = list(team_list_input) # Use a local copy for manipulation

    if not local_teams:
        return []

    n_orig = len(local_teams)
    if n_orig == 0:
        return []

    if n_orig % 2 != 0:
        local_teams.append("BYE") # Add a dummy team for even scheduling

    n = len(local_teams)

    final_schedule = []

    for _round_idx in range(n - 1): # n-1 rounds for n teams
        round_matches = []
        for i in range(n // 2):
            team1 = local_teams[i]
            team2 = local_teams[n - 1 - i]
            if team1 != "BYE" and team2 != "BYE":
                round_matches.append((team1, team2))
        final_schedule.extend(round_matches)

        # Rotate teams for the next round (keeping the first team fixed)
        if n > 2: # Rotation makes sense for 3+ teams.
            # Remove the last element from position 1 onwards and insert it at position 1.
            # Effectively: local_teams[0] is fixed. local_teams[1:] is rotated.
            fixed_element = local_teams[0]
            rotating_part = local_teams[1:]

            last_of_rotating = rotating_part.pop()
            rotating_part.insert(0, last_of_rotating)

            local_teams = [fixed_element] + rotating_part

    return final_schedule

# League Matches
scheduled_matches = generate_round_robin_schedule(teams)

print("\nGenerated Match Schedule:")
for idx, match in enumerate(scheduled_matches):
    print(f"Match {idx+1}: {match[0].upper()} vs {match[1].upper()}")
print("-" * 30) # Separator

for team1, team2 in scheduled_matches:
        print(f"\nMatch: {team1.upper()} vs {team2.upper()}")
        
        try:
            input("Press Enter to start the match...")
            
            print(random.choice(commentary_lines['start']))
            
            resList = game(False, team1, team2)

            # Display ball-by-ball and innings summary for both innings
            for innings, team_key, runs_key, balls_key, bat_tracker_key, bowl_tracker_key in [
                ('innings1Log', 'innings1BatTeam', 'innings1Runs', 'innings1Balls', 'innings1Battracker', 'innings1Bowltracker'),
                ('innings2Log', 'innings2BatTeam', 'innings2Runs', 'innings2Balls', 'innings2Battracker', 'innings2Bowltracker')
            ]:
                display_ball_by_ball(
                    resList[innings],
                    1 if innings == 'innings1Log' else 2,
                    resList[team_key],
                    resList[runs_key],
                    resList[balls_key],
                    max([event['wickets'] for event in resList[innings]], default=0),
                    resList[bat_tracker_key],
                    resList[bowl_tracker_key]
                )

            print(f"\nResult: {resList['winMsg']}")
            print(random.choice(commentary_lines['end']))

            # Track batting/bowling format win
            # resList['winner'] will be the actual winner's name (even after a Super Over) or 'tie'
            # resList['innings1BatTeam'] is the team that batted first in the main match.

            if resList['winner'] != "tie": # A definitive winner was decided (possibly via Super Over)
                if resList['winner'] == resList['innings1BatTeam']:
                    battingf += 1 # Team batting first won
                else:
                    # This means team batting second won (either in main chase or via Super Over)
                    bowlingf += 1 # Team bowling first / batting second won
            # If resList['winner'] IS "tie" (e.g., if Super Over itself was tied and no further tie-break implemented),
            # then battingf/bowlingf are not incremented, which is correct as neither team "won" by batting/bowling first/second.

            # Update batting stats
            for bat_map in [('innings1Battracker', 'innings1BatTeam'), ('innings2Battracker', 'innings2BatTeam')]:
                bat_tracker = resList[bat_map[0]]
                for player in bat_tracker:
                    if player not in battingInfo:
                        battingInfo[player] = copy.deepcopy(bat_tracker[player])
                        battingInfo[player]['innings'] = 1
                        battingInfo[player]['scoresArray'] = [int(battingInfo[player]['runs'])]
                    else:
                        battingInfo[player]['balls'] += bat_tracker[player]['balls']
                        battingInfo[player]['runs'] += bat_tracker[player]['runs']
                        battingInfo[player]['ballLog'] += bat_tracker[player]['ballLog']
                        battingInfo[player]['innings'] += 1
                        battingInfo[player]['scoresArray'].append(int(bat_tracker[player]['runs']))

            # Update bowling stats
            for bowl_map in [('innings1Bowltracker',), ('innings2Bowltracker',)]:
                bowl_tracker = resList[bowl_map[0]]
                for player in bowl_tracker:
                    if player not in bowlingInfo:
                        bowlingInfo[player] = copy.deepcopy(bowl_tracker[player])
                        bowlingInfo[player]['matches'] = 1
                    else:
                        bowlingInfo[player]['balls'] += bowl_tracker[player]['balls']
                        bowlingInfo[player]['runs'] += bowl_tracker[player]['runs']
                        bowlingInfo[player]['ballLog'] += bowl_tracker[player]['ballLog']
                        bowlingInfo[player]['wickets'] += bowl_tracker[player]['wickets']
                        bowlingInfo[player]['noballs'] = bowlingInfo[player].get('noballs', 0) + bowl_tracker[player].get('noballs', 0) # Aggregate noballs
                        bowlingInfo[player]['matches'] += 1

            # Points Table Update
            teamA = resList['innings1BatTeam']
            teamB = resList['innings2BatTeam']
            teamARuns, teamABalls = resList['innings1Runs'], resList['innings1Balls']
            teamBRuns, teamBBalls = resList['innings2Runs'], resList['innings2Balls']
            winner = resList['winner']
            loser = team1 if winner == team2 else team2

            for t in [team1, team2]:
                points[t]['P'] += 1

            if winner == "tie":
                for t in [team1, team2]:
                    points[t]['T'] += 1
                    points[t]['pts'] += 1
            else:
                points[winner]['W'] += 1
                points[loser]['L'] += 1
                points[winner]['pts'] += 2

            points[teamA]['runsScored'] += teamARuns
            points[teamB]['runsScored'] += teamBRuns
            points[teamA]['runsConceded'] += teamBRuns
            points[teamB]['runsConceded'] += teamARuns
            points[teamA]['ballsFaced'] += teamABalls
            points[teamB]['ballsFaced'] += teamBBalls
            points[teamA]['ballsBowled'] += teamBBalls
            points[teamB]['ballsBowled'] += teamABalls

            display_points_table()
            display_top_players()

            # Pause after match to keep console open
            input("Press Enter to continue to the next match...")

        except Exception as e:
            print(f"Error during match {team1.upper()} vs {team2.upper()}: {str(e)}")
            input("Press Enter to continue or Ctrl+C to exit...")
            continue

# POINTS TABLE (Final)
display_points_table()

# === PLAYOFFS ===
def playoffs(team1, team2, matchtag):
    print(f"\n{matchtag.upper()} - {team1.upper()} vs {team2.upper()}")
    try:
        input("Press Enter to start the playoff match...")
        print(random.choice(commentary_lines['start']))
        
        res = game(False, team1.lower(), team2.lower(), matchtag)
        
        for innings, team_key, runs_key, balls_key, bat_tracker_key, bowl_tracker_key in [
            ('innings1Log', 'innings1BatTeam', 'innings1Runs', 'innings1Balls', 'innings1Battracker', 'innings1Bowltracker'),
            ('innings2Log', 'innings2BatTeam', 'innings2Runs', 'innings2Balls', 'innings2Battracker', 'innings2Bowltracker')
        ]:
            display_ball_by_ball(
                res[innings],
                1 if innings == 'innings1Log' else 2,
                res[team_key],
                res[runs_key],
                res[balls_key],
                max([event['wickets'] for event in res[innings]], default=0),
                res[bat_tracker_key],
                res[bowl_tracker_key]
            )
        
        print(f"\nResult: {res['winMsg'].upper()}")
        print(random.choice(commentary_lines['end']))

        winner = res['winner']
        loser = team1 if winner == team2 else team2

        for bat_map in ['innings1Battracker', 'innings2Battracker']:
            tracker = res[bat_map]
            for player in tracker:
                if player not in battingInfo:
                    battingInfo[player] = copy.deepcopy(tracker[player])
                    battingInfo[player]['innings'] = 1
                    battingInfo[player]['scoresArray'] = [int(tracker[player]['runs'])]
                else:
                    battingInfo[player]['balls'] += tracker[player]['balls']
                    battingInfo[player]['runs'] += tracker[player]['runs']
                    battingInfo[player]['ballLog'] += tracker[player]['ballLog']
                    battingInfo[player]['innings'] += 1
                    battingInfo[player]['scoresArray'].append(int(tracker[player]['runs']))

        for bowl_map in ['innings1Bowltracker', 'innings2Bowltracker']:
            tracker = res[bowl_map]
            for player in tracker:
                if player not in bowlingInfo:
                    bowlingInfo[player] = copy.deepcopy(tracker[player])
                    bowlingInfo[player]['matches'] = 1
                else:
                    bowlingInfo[player]['balls'] += tracker[player]['balls']
                    bowlingInfo[player]['runs'] += tracker[player]['runs']
                    bowlingInfo[player]['ballLog'] += tracker[player]['ballLog']
                    bowlingInfo[player]['wickets'] += tracker[player]['wickets']
                    bowlingInfo[player]['noballs'] = bowlingInfo[player].get('noballs', 0) + tracker[player].get('noballs', 0) # Aggregate noballs for playoffs
                    bowlingInfo[player]['matches'] += 1

        display_points_table()
        display_top_players()

        # Pause after playoff match
        input("Press Enter to continue...")

        return winner, loser

    except Exception as e:
        print(f"Error during {matchtag.upper()}: {str(e)}")
        input("Press Enter to continue or Ctrl+C to exit...")
        return team1, team2  # Default to team1 as winner to continue playoffs

# PLAYOFF SEQUENCE
pointsTabulate = sorted(
    [[team, points[team]['pts'], (points[team]['runsScored'] / points[team]['ballsFaced']) * 6 - (points[team]['runsConceded'] / points[team]['ballsBowled']) * 6]
     for team in points],
    key=lambda x: (x[1], x[2]), reverse=True
)
q1 = [pointsTabulate[0][0], pointsTabulate[1][0]]
elim = [pointsTabulate[2][0], pointsTabulate[3][0]]

finalists = []

winnerQ1, loserQ1 = playoffs(q1[0], q1[1], "Qualifier 1")
finalists.append(winnerQ1)

winnerElim, _ = playoffs(elim[0], elim[1], "Eliminator")

winnerQ2, _ = playoffs(winnerElim, loserQ1, "Qualifier 2")
finalists.append(winnerQ2)

finalWinner, _ = playoffs(finalists[0], finalists[1], "Final")
print(f"\n🏆 {finalWinner.upper()} WINS THE IPL!!!")

# === SAVE FINAL STATS ===
battingTabulate = []
for b in battingInfo:
    c = battingInfo[b]
    outs = sum(1 for bl in c['ballLog'] if "W" in bl)
    avg = round(c['runs'] / outs, 2) if outs else "NA"
    sr = round((c['runs'] / c['balls']) * 100, 2) if c['balls'] else "NA"
    battingTabulate.append([b, c['innings'], c['runs'], avg, max(c['scoresArray']), sr, c['balls']])

battingTabulate = sorted(battingTabulate, key=lambda x: x[2], reverse=True)

bowlingTabulate = []
for b in bowlingInfo:
    c = bowlingInfo[b]
    overs = f"{c['balls'] // 6}.{c['balls'] % 6}" if c['balls'] else "0"
    economy = round((c['runs'] / c['balls']) * 6, 2) if c['balls'] else "NA"
    noballs = c.get('noballs', 0)
    bowlingTabulate.append([b, c['wickets'], overs, c['runs'], noballs, economy])

bowlingTabulate = sorted(bowlingTabulate, key=lambda x: x[1], reverse=True)

with open(os.path.join(dir_path, "batStats.txt"), "w") as f:
    sys.stdout = f
    print(tabulate(battingTabulate, headers=["Player", "Innings", "Runs", "Average", "Highest", "SR", "Balls"], tablefmt="grid"))
    sys.stdout = sys.__stdout__

with open(os.path.join(dir_path, "bowlStats.txt"), "w") as f:
    sys.stdout = f
    print(tabulate(bowlingTabulate, headers=["Player", "Wickets", "Overs", "Runs Conceded", "NB", "Economy"], tablefmt="grid"))
    sys.stdout = sys.__stdout__

print("bat", battingf, "bowl", bowlingf)
input("\nPress Enter to exit...")