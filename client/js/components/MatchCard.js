export default class MatchCard extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const template = document.getElementById("match-card");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
    this.classList.add(
      "col-sm",
      "w-100",
      "justify-content-between",
      "align-items-center",
      "d-flex",
      "mt-3",
      "rounded-3",
      "p-4",
      "border",
      "border-2",
      "border-dark",
      "font-weight-bold",
    );

    const match = JSON.parse(this.getAttribute("match"));

    const players = match.gamers.map(gamer => gamer.username)
    const scores = match.gamers.map(gamer => gamer.score)

    const winner = match.gamers.find(gamer => gamer.won === true)?.username;

    const playersTexts = document.createElement('div')
    playersTexts.innerText = players.join(', ')
    this.appendChild(playersTexts)

    const playersScores = document.createElement('div')
    playersScores.innerText = scores.join(' - ')
    this.appendChild(playersScores)

    const playersAvatarsContainer = document.createElement('div')

    for(const gamer of match.gamers) {
      const image = document.createElement("img")
      image.src = gamer.avatar
      image.classList.add('rounded-circle')
      if(gamer.won) {
        image.classList.add('border', 'border-5', 'border-success')
      }
      image.style = "width: 50px; height: 50px; margin-left: -20px;"
      playersAvatarsContainer.appendChild(image)
    }

    this.appendChild(playersAvatarsContainer)
  }
}

customElements.define("match-card", MatchCard);