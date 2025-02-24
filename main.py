from fasthtml.common import *
import random
import json
app, rt = fast_app()
multiplication_range = range(2, 11)

def get_problem_weights(request):
    """Retrieve weights from cookies or initialize them."""
    weights = {
        (a, b): float(request.cookies.get(f"{a}x{b}", 1.0))
        for a in multiplication_range for b in multiplication_range
    }
    return weights

def select_problem(weights):
    """Select a problem (num1, num2) based on weighted probabilities."""
    problems, probs = zip(*weights.items())
    num1, num2 = random.choices(problems, weights=probs, k=1)[0]
    answer = num1 * num2
    return num1, num2, answer

def generate_problem_ui(num1, num2, answer, correct, incorrect):
    content = Div(
        Div(f"{correct} - {incorrect}", id="scoreboard", cls="scoreboard"),
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
        ), id="content"
    )
    return content
# def generate_problem_ui(num1, num2, answer, correct, incorrect):
#     """Generate a new problem UI as a FastHTML response."""
#     return Div(
#         id="content",
#         children=[
#             Div(f"{correct} - {incorrect}", id="scoreboard", cls="scoreboard"),
#             Div(
#                 Div(
#                     Div(
#                         P(f"{num1} × {num2}", style="font-size: 3.5em; text-align: center;"), 
#                         cls="card-front"
#                     ),
#                     Div(
#                         P(str(answer), style="font-size: 3.5em; text-align: center;", id="problem-answer"),
#                         Div(
#                             Button("✓", 
#                                    cls="check-button", 
#                                    hx_post=f"/correct?num1={num1}&num2={num2}", 
#                                    hx_target="#content", 
#                                    hx_swap="outerHTML"),
#                             Button("✗", 
#                                    cls="x-button", 
#                                    hx_post=f"/incorrect?num1={num1}&num2={num2}", 
#                                    hx_target="#content", 
#                                    hx_swap="outerHTML"),
#                             cls="button-container"
#                         ),
#                         cls="card-back"
#                     ),
#                     cls="card",
#                     onclick="flipCard()"
#                 ),
#                 cls="card-container"
#             )
#         ]
#     )

@rt("/")
def get(request):
    correct = int(request.cookies.get('correct', 0))
    incorrect = int(request.cookies.get('incorrect', 0))

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
        }
    """

    # Add JavaScript to handle the flip and generate new problem
    script = """
        let correctScore = parseInt(document.cookie.match(/correct=(\d+)/)?.[1] || '0');
        let incorrectScore = parseInt(document.cookie.match(/incorrect=(\d+)/)?.[1] || '0');

        function updateScore() {
            document.getElementById('scoreboard').textContent = `${correctScore} - ${incorrectScore}`;
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
    """

    # Create the scoreboard and card structure
    content = generate_problem_ui(num1, num2, answer, correct, incorrect)
    
    return Titled("Sofia's Tablas", 
                 Style(style),  
                 Script(script), 
                 content)


@app.post("/correct")
def correct(request,  num1: int, num2: int):
    # update correct scoreo
    print(request.cookies)
    correct = int(request.cookies.get('correct', 0)) + 1
    incorrect = int(request.cookies.get('incorrect', 0))
    
    # Create a new response with updated UI
    weights = get_problem_weights(request)
    weights[(num1, num2)] = max(0.2, weights[(num1, num2)] * 0.8)
    
    # Get new problem
    new_num1, new_num2, new_answer = select_problem(weights)
    
    content = generate_problem_ui(new_num1, new_num2, new_answer, correct, incorrect)

    resp = Response(to_xml(content))
    resp.set_cookie("correct", str(correct))
    resp.set_cookie(f"{num1}x{num2}", str(weights[(num1, num2)]))
    return resp

@app.post("/incorrect")
def incorrect(request, num1: int, num2: int):
    correct = int(request.cookies.get('correct', 0))
    incorrect = int(request.cookies.get('incorrect', 0)) + 1
    
    weights = get_problem_weights(request)
    weights[(num1, num2)] = min(10.0, weights[(num1, num2)] * 2.4)  # Increase weight (max 5)
    new_num1, new_num2, new_answer = select_problem(weights)

    content = generate_problem_ui(new_num1, new_num2, new_answer, correct, incorrect)
    resp = Response(to_xml(content))
    resp.set_cookie("correct", str(correct))
    resp.set_cookie("incorrect", str(incorrect))
    resp.set_cookie(f"{num1}x{num2}", str(weights[(num1, num2)]))
    return resp


serve()
