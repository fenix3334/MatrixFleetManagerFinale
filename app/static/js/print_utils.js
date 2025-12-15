/*
 * Funzioni di supporto per la stampa.
 *
 * Questo script definisce una funzione per stampare solo l'area selezionata
 * dell'interfaccia. L'utente può utilizzare il mouse per selezionare una
 * porzione di testo o elementi della pagina e premere il pulsante "Stampa
 * selezione" per generare un'anteprima contenente solo quella parte.
 */

function printSelectedArea() {
    // Recupera la selezione corrente effettuata dall'utente
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || !selection.toString().trim()) {
        alert('Seleziona un\'area della pagina da stampare con il mouse.');
        return;
    }

    // Clona i nodi selezionati. Utilizziamo cloneContents per preservare
    // la struttura HTML (incluse tabelle, formattazioni, ecc.).
    const range = selection.getRangeAt(0);
    const clonedSelection = range.cloneContents();

    // Apri una nuova finestra dove inseriremo il contenuto selezionato
    const printWindow = window.open('', '', 'width=800,height=600');
    if (!printWindow) {
        alert('Impossibile aprire la finestra di stampa. Assicurati che i popup siano consentiti.');
        return;
    }

    printWindow.document.open();
    printWindow.document.write('<!DOCTYPE html><html><head><title>Stampa selezione</title>');

    // Copia tutti i fogli di stile presenti nella pagina corrente. Questo
    // garantisce che il contenuto selezionato mantenga lo stesso layout.
    const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
    stylesheets.forEach(link => {
        // Alcuni fogli di stile potrebbero essere caricati con URL assoluto; utilizziamo href.
        printWindow.document.write(`<link rel="stylesheet" href="${link.href}">`);
    });

    // Applichiamo uno stile di stampa base che nasconde header, footer e
    // pulsanti di controllo. Questo specchierà il comportamento definito in
    // base.html per la stampa completa.
    printWindow.document.write(
        '<style>@media print {\n' +
        '  /* Nasconde elementi non necessari nella stampa selezionata */\n' +
        '  .matrix-header, .matrix-footer, .print-actions, .user-info, .report-controls { display: none !important; }\n' +
        '  body { margin: 0; padding: 0; }\n' +
        '  .main-content { padding: 0; margin: 0; width: 100%; }\n' +
        '}\n</style>'
    );
    printWindow.document.write('</head><body>');

    // Inseriamo il contenuto selezionato all'interno del corpo del nuovo documento
    printWindow.document.body.appendChild(clonedSelection);

    printWindow.document.write('</body></html>');
    printWindow.document.close();

    // Focalizziamo e inviamo il comando di stampa. Chiudiamo la finestra al termine.
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}