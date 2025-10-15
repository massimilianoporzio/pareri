document.addEventListener("DOMContentLoaded", function () {
  const formsetTable = document.getElementById("datorelavorosede_set-group");

  if (formsetTable) {
    formsetTable.addEventListener("change", function (event) {
      const clickedCheckbox = event.target;

      // Assicurati che l'elemento cliccato sia una checkbox "is_sede_legale"
      if (
        clickedCheckbox.name.includes("is_sede_legale") &&
        clickedCheckbox.type === "checkbox"
      ) {
        if (clickedCheckbox.checked) {
          // Seleziona solo le checkbox all'interno del formset corrente
          const allCheckboxes = formsetTable.querySelectorAll(
            'input[name*="is_sede_legale"]',
          );

          allCheckboxes.forEach((checkbox) => {
            // Deseleziona le altre checkbox
            if (checkbox !== clickedCheckbox) {
              checkbox.checked = false;
            }
          });
        }
      }
    });
  }
});
