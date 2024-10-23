function scrollToTop(){
  window.scrollTo(0,0)
}

/*** Cookie message ***/
let cookiesOfDocument = document.cookie;

if (document.getElementById("cookies-banner")) {
  // cookies message
  let cookiesMessage = document.getElementById("cookies-banner");
  // console.log(cookiesMessage);

  function acceptCookies() {
    // Cookie message disappears
    cookiesMessage.classList.add("hidden");
    // and the acceptance cookie is created
    document.cookie = "cookies=accepted; path=/; samesite=strict; max-age=31536000";
  }

  // if there's a cookie named cookies (no matter the value)
  if (document.cookie.indexOf('cookies=') != "-1") {
    // we want the cookiesMessage to not show
    cookiesMessage.classList.add("hidden");
  };

  // Accepting and denying with keycaps - Esc and Enter
  let acceptCookiesButton = document.getElementById("cookies-accept");
  let denyCookiesButton = document.getElementById("cookies-deny");

  document.addEventListener("keydown", event => {
    if (event.key === "Enter") {
      // console.log("You pressed Enter Key");
      acceptCookiesButton.click();
    }
    else if (event.key === "Escape") {
      // console.log("You pressed Esc Key");
      denyCookiesButton.click();
    }
  });

  // Close the message when clicking on an option & create a cookie
  acceptCookiesButton.addEventListener("click", function(){
    acceptCookies();
  });

  denyCookiesButton.addEventListener("click", function(){
    cookiesMessage.classList.add("hidden");
    document.cookie = "cookies=denied; path=/; samesite=strict; max-age=31536000";
  })

  // Close the message when scrolling the page and create an acceptance cookie
  window.addEventListener('scroll', function() {
    var scrollNumber = window.scrollY;

    // If the user scrolls enough, 800px in this case
    if (scrollNumber >= 400) {
      acceptCookies();
    }
  });

  // // Close the message when the user navigates to another page and create an acceptance cookie
  // var myReferer = document.referrer;

  // // In case the user comes from our own website -> and so is navigating already
  // if (myReferer.indexOf("https://codi.coop/") != "-1") { // https://codi.coop/   http://localhost/
  //   // console.log("you've been here before!")
  //   acceptCookies();
  // }
}
