import router from "../utilities/router.js";
import fetching from "../utilities/fetching.js";


export default class Navbar extends HTMLElement {
  constructor() {
    super();
  }
  connectedCallback() {
    const template = document.getElementById("my-navbar");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
    this.classList.add(
      "d-flex",
      "justify-content-between",
      "align-items-center",
      "w-100",
      "px-5",
      "py-2",
    );

    const handleLink = (event) => {
      event.preventDefault();
      const url = event.target.getAttribute("href");
      router.go(url, "", "add");
    };

    const logo = this.querySelector(".logo");

    logo.addEventListener("click", handleLink);

    fetching(`https://${window.ft_transcendence_host}/player/`).then((res) => {
      this.querySelector(".avatar").setAttribute("src", res.gamer.avatar);
    });

  }
}

customElements.define("my-navbar", Navbar);
