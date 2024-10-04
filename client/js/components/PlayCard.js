import router from "../utilities/router.js";

export default class PlayCard extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const template = document.getElementById("play-card");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
    this.classList.add(
      "d-flex",
      "justify-content-center",
      "align-items-center",
      "flex-column",
      "rounded-5",
      "pb-3",
    );

    const play_online = this.querySelector(".play-online");
    const play_offline = this.querySelector(".play-offline");
    const play_tournament = this.querySelector(".play-tournament");
    const game = this.getAttribute("game");

    let gameRoute;
    gameRoute = "/game/";
    play_online.addEventListener("click", () => {
      router.go(gameRoute, `?game=${game}&mode=two`, "add");
    });
    play_offline.addEventListener("click", () => {
      router.go(gameRoute, `?game=${game}&mode=coop`, "add");
    });
    play_tournament.addEventListener("click", () => {
      window.location.href = "/tournaments";
    });
  }
}

customElements.define("play-card", PlayCard);
