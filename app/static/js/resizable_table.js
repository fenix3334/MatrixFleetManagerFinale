/*
 * resizable_table.js
 *
 * This script enables column resizing functionality for tables that have
 * the CSS class ``resizable-table``. It appends a small handle to the
 * right edge of each header cell (<th>) that the user can drag with the
 * left mouse button to adjust the column width. The resize action is
 * performed on the header itself, allowing the column to expand or
 * contract in real time, similar to spreadsheet applications. The
 * script runs after the page has loaded and will automatically apply
 * to any matching tables present in the DOM.
 */

(function() {
    function initResizableTables() {
        const tables = document.querySelectorAll('table.resizable-table');
        tables.forEach(table => {
            // Use automatic table layout to respect column widths
            table.style.tableLayout = 'fixed';
            table.style.width = '100%';
            const headers = table.querySelectorAll('th');
            headers.forEach((th) => {
                // Ensure relative positioning for the header cell so the handle can be positioned
                th.style.position = th.style.position || 'relative';
                const resizer = document.createElement('div');
                resizer.className = 'resizer';
                th.appendChild(resizer);

                let startX = 0;
                let startWidth = 0;

                resizer.addEventListener('mousedown', function(e) {
                    startX = e.pageX;
                    startWidth = th.getBoundingClientRect().width;
                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                    e.preventDefault();
                });

                function onMouseMove(e) {
                    const dx = e.pageX - startX;
                    const newWidth = startWidth + dx;
                    // Set a minimum width to prevent collapsing the column
                    if (newWidth > 30) {
                        th.style.width = newWidth + 'px';
                    }
                }

                function onMouseUp() {
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                }
            });
        });
    }
    // Initialize on DOMContentLoaded or immediately if already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initResizableTables);
    } else {
        initResizableTables();
    }
})();