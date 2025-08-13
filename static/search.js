

document.addEventListener('DOMContentLoaded', function() {
    // get search input
    const searchInput = document.getElementById("course_search");
    // get table
    const tableRows = document.querySelectorAll("tbody tr");

    // search for changes to search input
    searchInput.addEventListener("keyup", function () {
        // define search input every key up
        const searchTerm = searchInput.value.toLowerCase();

        // i did not know this method existed hitherto ¯\_( ͡° ͜ʖ ͡°)_/¯
        tableRows.forEach(row => {
            // index starts at 0 btw
            const class_id = row.cells[0].textContent.toLowerCase();
            const course = row.cells[1].textContent.toLowerCase();
            const days = row.cells[3].textContent.toLowerCase();
            const time = row.cells[4].textContent.toLowerCase();
            
            // just compare table rows to search term
            if (
                class_id.includes(searchTerm) ||
                course.includes(searchTerm) ||
                days.includes(searchTerm) ||
                time.includes(searchTerm)
            ) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }); 
    });
});