import fetching from "../utilities/fetching.js";

export default class MatchHistory extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const template = document.getElementById("match-history");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
    this.classList.add(
      // "col-xs-12",
      // "gap-2",
      // "px-0",
      // "rounded-5",
    );

    fetching(`https://${window.ft_transcendence_host}/player/matches/`).then((data) => {
      const matches = data.matches;
      if (matches.length === 0) {
        this.textContent = "No matches found";
      }
      for (const match of matches) {
        const row = document.createElement("div");
        row.classList.add(
          "d-flex",
          "flex-wrap",
          "justify-content-around",
          "p-2",
          "gap-1",
        );
        const match_card_elem = document.createElement("match-card");
        match_card_elem.setAttribute("match", JSON.stringify(match));
        row.appendChild(match_card_elem);
        this.appendChild(row);
      }
    });
  }
}

customElements.define("match-history", MatchHistory);
