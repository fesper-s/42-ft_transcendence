export let wsTwo;
let TwoPressKey = true;

function setPlayerData(data) {
  const avatar_left = data["padd_left"]["avatar"];
  const avatar_right = data["padd_right"]["avatar"];
  const username_left = data["padd_left"]["username"];
  const username_right = data["padd_right"]["username"];
  const pong_players_elem = document.querySelector(".pong-players");
  let player_elem;
  //TODO: alinhar foto e texto e colocar pontuação máxima 7
  player_elem = document.createElement("div");
  player_elem.style.display = "flex";
  player_elem.style.paddingBottom = "10px";
  player_elem.style.paddingTop = "5px"
  player_elem.style.justifyContent = "center";
  player_elem.style.alignItems = "center";
  player_elem.innerHTML = `
    <h1 style="font-size: 20px; margin-right: 8px">${username_left}</h1>
    <img src="${avatar_left}" alt="avatar" referrerpolicy="no-referrer">
  `;
  player_elem.querySelector("img").style.width = "30px";
  player_elem.querySelector("img").style.borderRadius = "50%";
  pong_players_elem.append(player_elem);
  player_elem = document.createElement("div");
  player_elem.style.display = "flex";
  player_elem.style.paddingBottom = "10px";
  player_elem.style.paddingTop = "5px"
  player_elem.style.justifyContent = "center";
  player_elem.style.alignItems = "center";
  player_elem.innerHTML = `
    <img style="margin-right: 8px; align-items: self-start" src="${avatar_right}" alt="avatar" referrerpolicy="no-referrer">
    <h1 style="font-size: 20px">${username_right}</h1>
  `;
  player_elem.querySelector("img").style.width = "30px";
  player_elem.querySelector("img").style.borderRadius = "50%";
  pong_players_elem.appendChild(player_elem);
}
export function runPongTwoGame(canvas, ctx, match_id) {
  wsTwo = new WebSocket(
    `wss://${window.ft_transcendence_host}/ws/matchmaking/2/${!match_id ? "" : match_id + "/"}`,
  );
  canvas.width = 1920;
  canvas.height = 1080;
  const ball = new Ball([canvas.width / 2, canvas.height / 2], 20);
  const paddle1 = new Paddle([60, canvas.height / 2 - 100], [40, 200]);
  const paddle2 = new Paddle([canvas.width - 100, canvas.height / 2 - 100], [40, 200]);
  ctx.fillStyle = "white";
  ctx.font = "100px monospace";
  ctx.textAlign = "center";
  let i = 0;
  const intervalId = setInterval(() => {
    i++;
    ctx.font = "100px Lobster"
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillText(
      "Waiting",
      canvas.width / 2,
      canvas.height / 2.5,
    );
    ctx.font = "24px Inter"
    ctx.fillText(
        "We’re waiting for another player to join the game",
        canvas.width / 2,
        canvas.height / 2,
    );

    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 1.7);
    ctx.rotate((i * Math.PI) / 5);
    ctx.font = "200px Inter";
    ctx.fillText(
        ".",
        0,
        0,
    );
    ctx.restore();

    if (i === 60) i = 0;
  }, 100);
  wsTwo.onmessage = function (e) {
    clearInterval(intervalId);
    if (e.data === "ALREADY IN GAME" || e.data === "ALREADY PLAYED") {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "white";
      ctx.font = "100px monospace";
      ctx.textAlign = "center";
      ctx.fillText(e.data, canvas.width / 2, canvas.height / 2);
      wsTwo.close();
      return;
    }
    let alreadyInGame = false;
    wsTwo = new WebSocket(
      `wss://${window.ft_transcendence_host}/ws/pong/${e.data}/2/${
        !match_id ? "" : match_id + "/"
      }`,
    );
    let pos;
    wsTwo.onmessage = function (e) {
      let tmp = JSON.parse(e.data);
      if (!alreadyInGame) {
        if (typeof tmp === "number") {
          pos = tmp;
          return;
        }
        setPlayerData(tmp);
        alreadyInGame = true;
      }
      if (typeof tmp === "string") {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillText(tmp, canvas.width / 2, canvas.height / 2);
        wsTwo.close();
        return;
      }
      ball.positionX = tmp["ball"].positionX;
      ball.positionY = tmp["ball"].positionY;
      paddle1.positionY = tmp["padd_left"]["info"].positionY;
      paddle2.positionY = tmp["padd_right"]["info"].positionY;
      paddle1.score = tmp["padd_left"]["info"]["score"];
      paddle2.score = tmp["padd_right"]["info"]["score"];
      gameLoop(canvas, ctx, ball, paddle1, paddle2, pos);
    };
  };
  if (TwoPressKey)
    window.addEventListener("keydown", function (e) {
      if (e.keyCode in keys && wsTwo.readyState != WebSocket.CLOSED) wsTwo.send(keys[e.keyCode]);
    });
  TwoPressKey = false;
}

export const keys = {
  38: "up",
  40: "down",
  87: "w",
  83: "s",
};

export class Paddle {
  constructor(position, size) {
    this.positionX = position[0];
    this.positionY = position[1];
    this.sizeX = size[0];
    this.sizeY = size[1];
    this.score = 0;
  }

  render(ctx, color = "#fff") {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(this.positionX, this.positionY, this.sizeX, this.sizeY, 10);
    ctx.stroke();
    ctx.fill();
  }
}

export class Ball {
  constructor(position, size) {
    this.positionX = position[0];
    this.positionY = position[1];
    this.size = size;
  }

  render(ctx) {
    ctx.beginPath();
    ctx.arc(this.positionX, this.positionY, this.size, 0, 2 * Math.PI);
    ctx.fillStyle = "white";
    ctx.fill();
  }
}

function RenderScore(ctx, canvas, right, left) {
  const rightX = canvas.width / 2 - 60;
  const leftX = canvas.width / 2 + 10;
  const rightWidth = ctx.measureText(right).width;
  const dashX = (rightX + rightWidth + leftX) / 2;

  ctx.fillStyle = "white";
  ctx.font = "bold 100px Inter";
  ctx.fillText(left, canvas.width / 2 - 60, 120);
  ctx.fillText('-', dashX, 120);
  ctx.fillText(right, canvas.width / 2 + 60, 120);
}

function gameLoop(canvas, ctx, ball, paddle1, paddle2, pos) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ball.render(ctx);
  if (pos === 1) paddle1.render(ctx, "#fff");
  else paddle1.render(ctx);
  if (pos === 2) paddle2.render(ctx, "#fff");
  else paddle2.render(ctx);
  RenderScore(ctx, canvas, paddle2.score, paddle1.score);
}
