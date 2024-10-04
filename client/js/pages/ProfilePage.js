import fetching from "../utilities/fetching.js";

export default class ProfilePage extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const template = document.getElementById("profile-template");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
    this.classList.add("my-page");

    fetching(`https://${window.ft_transcendence_host}/player/`).then((res) => {
      this.querySelector(".player-data .username").innerText = "Welcome, " + res.gamer.username;
      this.querySelector(".player-data .champions").innerText = res.gamer.champions;
      this.querySelector(".player-data .wins").innerText = res.gamer.wins;
      this.querySelector(".player-data .losses").innerText = res.gamer.losses;
    });
  }
}

customElements.define("profile-page", ProfilePage);