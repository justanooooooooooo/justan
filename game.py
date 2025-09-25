import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Green Dot Hunter", layout="wide")

st.title("🟢 Green Dot Hunter by Justan")

game_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Green Dot Hunter</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background: linear-gradient(#222, #555);
      overflow: hidden;
      user-select: none;
      color: white;
    }

    #game {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }

    .monster {
      position: absolute;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: limegreen;
      cursor: pointer;
      transition: transform 0.1s;
    }

    .monster:active {
      transform: scale(0.8);
    }

    #scoreboard {
      position: absolute;
      top: 10px;
      left: 10px;
      font-size: 1.5rem;
      background: rgba(0, 0, 0, 0.5);
      padding: 10px 20px;
      border-radius: 10px;
    }

    #timer {
      position: absolute;
      top: 10px;
      right: 10px;
      font-size: 1.5rem;
      background: rgba(0, 0, 0, 0.5);
      padding: 10px 20px;
      border-radius: 10px;
    }

    #game-over {
      display: none;
      position: absolute;
      top: 40%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 3rem;
      background: rgba(0, 0, 0, 0.9);
      padding: 40px;
      border-radius: 20px;
      text-align: center;
    }

    #restart {
      margin-top: 20px;
      font-size: 1rem;
      padding: 10px 20px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div id="game">
    <div id="scoreboard">Score: 0</div>
    <div id="timer">Time: 60</div>
    <div id="game-over">
      Game Over!<br>
      Final Score: <span id="final-score">0</span><br>
      <button id="restart">Play Again</button>
    </div>
  </div>

  <script>
    const game = document.getElementById('game');
    const scoreboard = document.getElementById('scoreboard');
    const timerDisplay = document.getElementById('timer');
    const gameOverScreen = document.getElementById('game-over');
    const finalScoreDisplay = document.getElementById('final-score');
    const restartBtn = document.getElementById('restart');

    let score = 0;
    let timeLeft = 60;
    let gameInterval;
    let spawnInterval;
    let spawnSpeed = 700; // 初始間隔 (毫秒)

    function randomPosition() {
      const x = Math.random() * (window.innerWidth - 80);
      const y = Math.random() * (window.innerHeight - 80);
      return { x, y };
    }

    function spawnMonster() {
      const { x, y } = randomPosition();
      const monster = document.createElement('div');
      monster.className = 'monster';
      monster.style.left = `${x}px`;
      monster.style.top = `${y}px`;

      monster.onclick = () => {
        score += 1;
        scoreboard.textContent = `Score: ${score}`;
        game.removeChild(monster);

        const feedback = document.createElement('div');
        feedback.textContent = "+1";
        feedback.style.position = "absolute";
        feedback.style.left = `${x}px`;
        feedback.style.top = `${y}px`;
        feedback.style.fontSize = "1.5rem";
        feedback.style.color = "lime";
        game.appendChild(feedback);
        setTimeout(() => feedback.remove(), 600);
      };

      game.appendChild(monster);
      setTimeout(() => {
        if (game.contains(monster)) game.removeChild(monster);
      }, 1500);
    }

    function startGame() {
      score = 0;
      timeLeft = 60;
      spawnSpeed = 700; // 重設初始速度
      scoreboard.textContent = 'Score: 0';
      timerDisplay.textContent = 'Time: 60';
      gameOverScreen.style.display = 'none';

      gameInterval = setInterval(() => {
        timeLeft--;
        timerDisplay.textContent = `Time: ${timeLeft}`;

        // 每 10 秒加快一次 (最小 300ms)
        if (timeLeft % 10 === 0 && spawnSpeed > 300) {
          spawnSpeed -= 100;
          clearInterval(spawnInterval);
          spawnInterval = setInterval(spawnMonster, spawnSpeed);
        }

        if (timeLeft <= 0) {
          endGame();
        }
      }, 1000);

      spawnInterval = setInterval(spawnMonster, spawnSpeed);
    }

    function endGame() {
      clearInterval(gameInterval);
      clearInterval(spawnInterval);
      document.querySelectorAll('.monster').forEach(monster => monster.remove());
      finalScoreDisplay.textContent = score;
      gameOverScreen.style.display = 'block';
    }

    restartBtn.onclick = startGame;
    window.onload = startGame;
  </script>
</body>
</html>
"""

components.html(game_html, height=700, scrolling=False)
