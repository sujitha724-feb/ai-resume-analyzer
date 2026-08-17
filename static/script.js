const fileInput = document.getElementById("resume");

if (fileInput) {

    fileInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        if (file.type !== "application/pdf") {

            alert("Please select a PDF file.");

            this.value = "";

        }

    });

}
