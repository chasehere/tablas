from fasthtml.common import *
import random

app, rt = fast_app()

@rt("/")
def get():
    # Generate random numbers for multiplication
    num1 = random.randint(2, 10)
    num2 = random.randint(2, 10)
    answer = num1 * num2

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
        let correctScore = 0;
        let incorrectScore = 0;

        function updateScore() {
            document.getElementById('scoreboard').textContent = `${correctScore} - ${incorrectScore}`;
        }

        function flipCard() {
            const card = document.querySelector('.card');
            card.classList.toggle('flipped');
            
            // If card is being flipped back to front, fetch new problem
            if (!card.classList.contains('flipped')) {
                window.location.reload();
            }
        }

        function handleAnswer(correct) {
            if (correct) {
                correctScore++;
            } else {
                incorrectScore++;
            }
            updateScore();
            setTimeout(flipCard, 500);  // Flip card after short delay
        }
    """

    # Create the scoreboard and card structure
    content = Div(
        Div("0 - 0", id="scoreboard", cls="scoreboard"),
        Div(
            Div(
                Div(P(f"{num1} × {num2}", style="font-size: 3.5em; text-align: center;"), cls="card-front"),
                Div(
                    P(str(answer), style="font-size: 3.5em; text-align: center;"),
                    Div(
                        Button("✓", cls="check-button", onclick="handleAnswer(true)"),
                        Button("✗", cls="x-button", onclick="handleAnswer(false)"),
                        cls="button-container"
                    ),
                    cls="card-back"
                ),
                cls="card",
                onclick="flipCard()"
            ),
            cls="card-container"
        )
    )
    
    return Titled("Sofia's Tablas", 
                 Style(style),  
                 Script(script), 
                 content)

serve()
