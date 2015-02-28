ZeroClipboard.config( { swfPath: "/static/swf/ZeroClipboard.swf" } );


$(function() {
    var client = new ZeroClipboard($(".copy-button"));

   $("table.tablesorter").tablesorter( { sortList: [[0,0]] } );
});
