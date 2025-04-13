from fasthtml.common import *
import random
app, rt = fast_app()

MAX_TABLE = 12
multiplication_range = range(2, MAX_TABLE + 1)

def get_problem_weights(request):
    """Retrieve weights from cookies or initialize them."""
    weights = {}
    for a in multiplication_range:
        for b in multiplication_range:
            # Sort factors to ensure a ≤ b so that 2×5 and 5×2 are treated as the same
            min_factor, max_factor = sorted([a, b])
            key = f"{min_factor}x{max_factor}"
            if key not in weights:
                weights[(min_factor, max_factor)] = float(request.cookies.get(key, 1.0))
    return weights

def set_problem_weight(response, num1, num2, weight):
    """Save a problem weight to cookies with sorted factors."""
    min_factor, max_factor = sorted([num1, num2])
    response.set_cookie(f"{min_factor}x{max_factor}", str(weight))
    return response

def select_problem(weights):
    """Select a problem (num1, num2) based on weighted probabilities."""
    problems, probs = zip(*weights.items())
    min_factor, max_factor = random.choices(problems, weights=probs, k=1)[0]
    
    # Randomly decide whether to show min_factor × max_factor or max_factor × min_factor
    if random.choice([True, False]) and min_factor != max_factor:
        num1, num2 = max_factor, min_factor
    else:
        num1, num2 = min_factor, max_factor
        
    answer = num1 * num2
    return num1, num2, answer


def get_total_problems():
    return int(len(multiplication_range) * (len(multiplication_range) + 1) / 2)  # 9x9 distinct problems (including symmetric ones only once)

def get_problems_left_to_learn(request):
    """Calculate the number of problems left to learn (weight < 0.3)."""
    total_problems = get_total_problems()
    weights = get_problem_weights(request)
    
    mastered = sum(1 for (_, _), weight in weights.items() if weight < 0.6)
    return total_problems - mastered

def generate_problem_ui(num1, num2, answer, correct, incorrect, left_to_learn):
    total_problems = get_total_problems()
    content = Div(
        Div(
            Span(f"{correct} - {incorrect}", cls="score-text"),
            Button("Report", id="report-button", cls="report-button", onclick="showTopProblems()"),
            id="scoreboard", cls="scoreboard", style="display: none;"  # Hide the scoreboard
        ),
        Div(id="top-problems", cls="top-problems"),
        Div(
            Div(
                Div(P(f"{num1} × {num2}", style="font-size: 3.5em; text-align: center;"), cls="card-front"),
                Div(
                    P(str(answer), style="font-size: 3.5em; text-align: center;"),
                    Div(
                        Button("✓", cls="check-button", hx_post=f"/correct?num1={num1}&num2={num2}", hx_target="#content"),
                        Button("✗", cls="x-button", hx_post=f"/incorrect?num1={num1}&num2={num2}", hx_target="#content"),
                        cls="button-container"
                    ),
                    cls="card-back"
                ),
                cls="card",
                onclick="flipCard()"
            ),
            cls="card-container"
        ),
        Div(f"Left to learn: {left_to_learn}/{total_problems}", cls="learn-counter"),
        id="content"
    )
    return content

@rt("/")
def get(request):
    correct = int(request.cookies.get('correct', 0))
    incorrect = int(request.cookies.get('incorrect', 0))
    left_to_learn = get_problems_left_to_learn(request)

    # get new problem
    weights = get_problem_weights(request)
    num1, num2, answer = select_problem(weights)

    # Add CSS for the flip animation and buttons
    style = """
        .card-container {
            perspective: 1000px;
            width: 400px;
            height: 300px;
            margin: 50px auto;
        }
        .card {
            position: relative;
            width: 100%;
            height: 100%;
            transform-style: preserve-3d;
            transition: transform 0.6s;
            cursor: pointer;
        }
        .card.flipped {
            transform: rotateY(180deg);
        }
        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            background: white;
        }
        .card-back {
            transform: rotateY(180deg);
            flex-direction: column;
        }
        .button-container {
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }
        .check-button, .x-button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 1.5em;
            cursor: pointer;
            transition: transform 0.1s;
        }
        .check-button {
            background-color: #4CAF50;
            color: white;
        }
        .x-button {
            background-color: #f44336;
            color: white;
        }
        .check-button:hover, .x-button:hover {
            transform: scale(1.1);
        }
        .scoreboard {
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 2em;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .score-text {
            margin-right: 5px;
        }
        .report-button {
            padding: 4px 10px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 0.6em;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .report-button:hover {
            background-color: #0b7dda;
        }
        .top-problems {
            position: fixed;
            top: 70px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            display: none;
            font-size: 1.2em;
            max-width: 200px;
        }
        .top-problems h3 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #333;
        }
        .top-problems ul {
            margin: 0;
            padding-left: 20px;
        }
        .top-problems li {
            margin-bottom: 5px;
        }
        .learn-counter {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            font-size: 1.3em;
            text-align: center;
        }
    """

    # Add JavaScript to handle the flip and generate new problem
    script = """
        let correctScore = parseInt(document.cookie.match(/correct=(\d+)/)?.[1] || '0');
        let incorrectScore = parseInt(document.cookie.match(/incorrect=(\d+)/)?.[1] || '0');

        function updateScore() {
            document.querySelector('.score-text').textContent = `${correctScore} - ${incorrectScore}`;
        }
        
        // Initialize score on page load
        updateScore();

        function flipCard() {
            const card = document.querySelector('.card');
            card.classList.toggle('flipped');
            
            // If card is being flipped back to front, fetch new problem
            // if (!card.classList.contains('flipped')) {
            //      window.location.reload();
            // }
        }

        function handleAnswer(correct) {
            const num1 = """ + str(num1) + """;
            const num2 = """ + str(num2) + """;
            if (correct) {
                correctScore++;
                fetch('/correct?num1=' + num1 + '&num2=' + num2, {
                    method: 'POST'
                });
            } else {
                incorrectScore++;
                fetch('/incorrect?num1=' + num1 + '&num2=' + num2, {
                    method: 'POST'
                });
            }
            updateScore();
            setTimeout(flipCard, 500);  // Flip card after short delay
        }

        function showTopProblems() {
            const topProblemsDiv = document.getElementById('top-problems');
            
            // If already showing, just toggle off and return
            if (topProblemsDiv.style.display === 'block') {
                topProblemsDiv.style.display = 'none';
                return;
            }
            
            // Show loading state
            topProblemsDiv.innerHTML = '<p>Loading...</p>';
            topProblemsDiv.style.display = 'block';
            
            // Fetch top problems
            fetch('/top_problems')
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        topProblemsDiv.innerHTML = '<h3>Great job!</h3><p>No difficult problems found.</p>';
                        return;
                    }
                    
                    let html = '<h3>Problems to Practice</h3><ul>';
                    
                    data.forEach(item => {
                        html += `<li>${item.problem}</li>`;
                    });
                    
                    html += '</ul>';
                    topProblemsDiv.innerHTML = html;
                })
                .catch(error => {
                    topProblemsDiv.innerHTML = '<p>Error loading problems</p>';
                    console.error('Error:', error);
                });
        }
        
        // Hide top problems when clicking outside
        document.addEventListener('click', function(event) {
            const topProblemsDiv = document.getElementById('top-problems');
            const reportButton = document.getElementById('report-button');
            
            if (event.target !== topProblemsDiv && 
                !topProblemsDiv.contains(event.target) && 
                event.target !== reportButton) {
                topProblemsDiv.style.display = 'none';
            }
        });
    """

    # Create the scoreboard and card structure
    content = generate_problem_ui(num1, num2, answer, correct, incorrect, left_to_learn)
    
    return Titled("Sofia's Tablas", 
                 Style(style),  
                 Script(script), 
                 content)


@app.post("/correct")
def correct(request, num1: int, num2: int):
    # update correct score
    correct = int(request.cookies.get('correct', 0)) + 1
    incorrect = int(request.cookies.get('incorrect', 0))
    
    # Create a new response with updated UI
    weights = get_problem_weights(request)
    min_factor, max_factor = sorted([num1, num2])
    weights[(min_factor, max_factor)] = max(0.2, weights[(min_factor, max_factor)] * 0.5)
    
    # Get new problem
    new_num1, new_num2, new_answer = select_problem(weights)
    
    # Calculate left to learn
    left_to_learn = get_problems_left_to_learn(request)
    
    content = generate_problem_ui(new_num1, new_num2, new_answer, correct, incorrect, left_to_learn)

    resp = Response(to_xml(content))
    resp.set_cookie("correct", str(correct))
    resp = set_problem_weight(resp, num1, num2, weights[(min_factor, max_factor)])
    return resp

@app.post("/incorrect")
def incorrect(request, num1: int, num2: int):
    correct = int(request.cookies.get('correct', 0))
    incorrect = int(request.cookies.get('incorrect', 0)) + 1
    
    weights = get_problem_weights(request)
    min_factor, max_factor = sorted([num1, num2])
    weights[(min_factor, max_factor)] = min(10.0, weights[(min_factor, max_factor)] * 2.4)  # Increase weight (max 10)
    new_num1, new_num2, new_answer = select_problem(weights)

    # Calculate left to learn
    left_to_learn = get_problems_left_to_learn(request)
    
    content = generate_problem_ui(new_num1, new_num2, new_answer, correct, incorrect, left_to_learn)
    resp = Response(to_xml(content))
    resp.set_cookie("correct", str(correct))
    resp.set_cookie("incorrect", str(incorrect))
    resp = set_problem_weight(resp, num1, num2, weights[(min_factor, max_factor)])
    return resp

@app.get("/top_problems")
def top_problems(request):
    """Return problems with weights > 1."""
    weights = get_problem_weights(request)
    
    # Filter problems with weight > 1 and sort by weight in descending order
    hard_problems = [(key, weight) for key, weight in weights.items() if weight > 1]
    sorted_problems = sorted(hard_problems, key=lambda x: x[1], reverse=True)
    
    # Format the problems
    result = []
    for (min_factor, max_factor), weight in sorted_problems:
        result.append({
            "problem": f"{min_factor}×{max_factor}",
            "weight": weight
        })
    
    # Return as JSON
    return JSONResponse(result)

serve()
