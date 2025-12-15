
// v1.25.8 - UI offset toggle (Style B)
(function(){
  var KEY = "mx.ui.offset.mode"; // "distant" | "compact"
  function apply(mode){
    document.body.classList.remove("ui-offset-distant","ui-offset-compact");
    if(mode === "compact") document.body.classList.add("ui-offset-compact");
    else document.body.classList.add("ui-offset-distant");
  }
  function current(){ var v = localStorage.getItem(KEY); return (v==="compact"||v==="distant")?v:"distant"; }
  function set(mode){ localStorage.setItem(KEY, mode); apply(mode); }
  function init(){
    apply(current());
    document.querySelectorAll("[data-ui-offset]").forEach(function(el){
      el.addEventListener("click", function(e){ e.preventDefault(); set(el.getAttribute("data-ui-offset")); });
    });
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.__mx_set_ui_offset=set;
})();
