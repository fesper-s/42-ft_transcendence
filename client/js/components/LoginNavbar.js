import router from "../utilities/router.js";

export default class LoginNavbar extends HTMLElement {
  constructor() {
    super();
  }
  connectedCallback() {
    const template = document.getElementById("login-navbar");
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
    const colorizer = this.querySelector(".colorizer.btn");
    const links = this.querySelectorAll(".link.btn");

    logo.addEventListener("click", handleLink);

    links.forEach((link) => {
      link.addEventListener("click", handleLink);
    });
  }
}

customElements.define("login-navbar", LoginNavbar);
