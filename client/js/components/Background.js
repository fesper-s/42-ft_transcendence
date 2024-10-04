export default class Background extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const template = document.getElementById("bg-beach");
    const component = template.content.cloneNode(true);
    this.appendChild(component);
  }
}

customElements.define("bg-beach", Background);