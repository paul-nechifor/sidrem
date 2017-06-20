function copyText(fromEl, toEl) {
  fromEl.addEventListener('keyup', () => {
    toEl.innerHTML = fromEl.innerHTML;
  }, false);
}

function byId(id) {
  return document.getElementById(id);
}

const sidrem = byId('sidrem-block');
const english = byId('english-block');

copyText(sidrem, english);
copyText(english, sidrem);
