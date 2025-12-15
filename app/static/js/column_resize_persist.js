
// v1.25.7 - Column width resize & persist (localStorage)
(function(){
  function keyFor(table){
    var path = location.pathname;
    var id = table.id || ("tbl-" + Array.prototype.indexOf.call(document.querySelectorAll("table.table"), table));
    return "mx.colwidths::" + path + "::" + id;
  }
  function loadWidths(table){
    try{
      var data = localStorage.getItem(keyFor(table));
      if(!data) return;
      var widths = JSON.parse(data);
      var ths = table.querySelectorAll("thead th");
      widths.forEach(function(w, i){
        if(ths[i] && w){ ths[i].style.width = w + "px"; }
      });
    }catch(e){}
  }
  function saveWidths(table){
    try{
      var ths = table.querySelectorAll("thead th");
      var widths = Array.prototype.map.call(ths, function(th){
        return Math.round(th.getBoundingClientRect().width);
      });
      localStorage.setItem(keyFor(table), JSON.stringify(widths));
    }catch(e){}
  }
  function makeResizable(table){
    var ths = table.querySelectorAll("thead th");
    ths.forEach(function(th){
      th.style.position = th.style.position || "relative";
      var handle = document.createElement("div");
      handle.className = "mx-col-resizer";
      handle.title = "Trascina per ridimensionare";
      handle.style.position = "absolute";
      handle.style.top = 0;
      handle.style.right = 0;
      handle.style.width = "6px";
      handle.style.cursor = "col-resize";
      handle.style.userSelect = "none";
      handle.style.height = "100%";
      handle.style.zIndex = 2;
      th.appendChild(handle);

      var startX, startW;
      function onMove(e){
        var dx = e.clientX - startX;
        var newW = Math.max(40, startW + dx);
        th.style.width = newW + "px";
      }
      function onUp(){
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        saveWidths(table);
      }
      handle.addEventListener("mousedown", function(e){
        e.preventDefault();
        startX = e.clientX;
        startW = th.getBoundingClientRect().width;
        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
      });
    });
  }
  function init(){
    var tables = document.querySelectorAll("table.table");
    tables.forEach(function(tbl){
      makeResizable(tbl);
      loadWidths(tbl);
      window.addEventListener("beforeunload", function(){ saveWidths(tbl); });
    });
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
