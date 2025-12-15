
// v1.26.0 - Topbar theme toggle (default vs geotab-like)
(function(){
  var KEY = "mx.ui.topbar.theme"; // values: "default" | "geotab"
  function apply(mode){
    document.body.classList.remove("topbar-geotab");
    if(mode === "geotab") document.body.classList.add("topbar-geotab");
  }
  function current(){
    var v = localStorage.getItem(KEY);
    return (v === "geotab" || v === "default") ? v : "geotab"; // default to geotab per richiesta
  }
  function set(mode){ localStorage.setItem(KEY, mode); apply(mode); }
  function init(){
    apply(current());
    document.querySelectorAll("[data-topbar-theme]").forEach(function(el){
      el.addEventListener("click", function(e){
        e.preventDefault();
        set(el.getAttribute("data-topbar-theme"));
      });
    });
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
  window.__mx_set_topbar_theme = set;
})();
