var element = document.getElementsByClassName("plyr__controls__item plyr__control");
var clickEvent = new MouseEvent("click", {
    "view": window,
    "bubbles": true,
    "cancelable": false
});

element.dispatchEvent(clickEvent);